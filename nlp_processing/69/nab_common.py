"""NAB 実センサーデータの読み込み・正解ラベルでの評価・可視化の共通処理。

3 系統（(a) 数値直接入力 / (b) 画像化→VLM / (c) TSFM+LLM）を同一データ・同一指標で
公正に比較できるよう、データ・正解・評価指標をこのモジュールに集約する。
"""

import csv
import json
import os
import re
import urllib.request
from datetime import datetime

import numpy as np
import yaml


def summary_from_flags(series, timestamps, flags):
    """検知された異常点（時刻・値）の要約テキストを組み立てる（説明層 LLM への入力）。"""
    idx = [i for i, f in enumerate(flags) if f]
    lines = [f"検知された異常点数: {len(idx)}", "異常点（時刻, 値）:"]
    lines += [f"- {timestamps[i]:%Y-%m-%d %H:%M}: 値={series[i]:.2f}" for i in idx]
    return "\n".join(lines)


def generate_report(summary, data_label, prompts_path, base_url, model, api_key, reasoning_effort=None):
    """検知結果の要約を LLM に渡し、運用向けの自然言語レポートを生成する（プロンプトは prompts.yaml）。"""
    from openai import OpenAI

    with open(prompts_path) as f:
        prompts = yaml.safe_load(f)
    kwargs = {"reasoning_effort": reasoning_effort} if reasoning_effort else {}
    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompts["report_system"]},
            {"role": "user", "content": prompts["report_user_template"].format(data_label=data_label, summary=summary)},
        ],
        temperature=0.0,  # 事実に忠実なレポートを狙い決定的に生成する
        **kwargs,
    )
    return resp.choices[0].message.content or ""


def extract_json_list(content):
    """LLM/VLM 応答から JSON 配列を頑健に取り出す。

    コードフェンス・前後の散文・{"anomalies": [...]} のような dict ラッパーに対応し、
    スキーマ逸脱時もクラッシュせず空配列を返す（無言の 0 検出を避けるため呼び出し側で警告する）。
    """
    if not content:
        return []
    m = re.search(r"\[.*\]", content, re.S)  # 最初の [ ... ] を抽出
    try:
        data = json.loads(m.group(0) if m else content)
    except json.JSONDecodeError:
        return None  # パース失敗（呼び出し側で警告）
    if isinstance(data, dict):  # {"anomalies": [...]} 等のラッパー
        for v in data.values():
            if isinstance(v, list):
                return v
        return []
    return data if isinstance(data, list) else []


def parse_dt_flexible(s):
    """VLM が返す時刻文字列を柔軟にパース（ISO の T 区切りや秒付きにも対応）。失敗時 None。"""
    s = str(s).strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


NAB_BASE = "https://raw.githubusercontent.com/numenta/NAB/master"
NAB_LABELS_URL = f"{NAB_BASE}/labels/combined_windows.json"
NAB_PRESETS = {
    "machine-temp": "realKnownCause/machine_temperature_system_failure.csv",
    "ambient-temp": "realKnownCause/ambient_temperature_system_failure.csv",
    "cpu": "realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv",
    "traffic-speed": "realTraffic/speed_7578.csv",
    "traffic-occupancy": "realTraffic/occupancy_6005.csv",
    "network": "realAWSCloudwatch/ec2_network_in_5abac7.csv",
}


def _download(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print(f"[download] {url} -> {path}")
        tmp = path + ".tmp"
        urllib.request.urlretrieve(url, tmp)
        os.replace(tmp, path)


def load_nab_dataset(key, data_dir="datasets/nab", downsample=1):
    """NAB のセンサーデータと既知異常区間ラベルを読み込む。

    Returns: values(np.float32), timestamps(list[datetime]), gt_windows(list[(start,end)])
    """
    nab_key = NAB_PRESETS.get(key, key)
    csv_path = os.path.join(data_dir, os.path.basename(nab_key))
    labels_path = os.path.join(data_dir, "combined_windows.json")
    _download(f"{NAB_BASE}/data/{nab_key}", csv_path)
    _download(NAB_LABELS_URL, labels_path)

    timestamps, values = [], []
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            timestamps.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
            values.append(float(row[1]))
    if downsample > 1:
        timestamps, values = timestamps[::downsample], values[::downsample]

    with open(labels_path) as f:
        windows = json.load(f).get(nab_key, [])
    gt_windows = [(datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S"), datetime.strptime(e[:19], "%Y-%m-%d %H:%M:%S")) for s, e in windows]
    return np.asarray(values, dtype=np.float32), timestamps, gt_windows


def gt_flags_from_windows(timestamps, gt_windows):
    """各点が既知異常区間内かどうかの正解ブールを返す。"""
    flags = np.zeros(len(timestamps), dtype=bool)
    for i, t in enumerate(timestamps):
        flags[i] = any(s <= t <= e for s, e in gt_windows)
    return flags


def evaluate(pred_flags, timestamps, gt_windows):
    """異常「区間」単位で Precision / Recall / F1 を算出する。

    本 Tip の 3 系統はいずれも系列全体を一度に見る**バッチ処理**なので、
    検出の早さを評価する NAB 公式スコア（ストリーミング検出器向け）は前提が合わない。
    ここでは「異常区間をいくつ当てたか」「誤検知をいくつ出したか」を素直に測る。

    - TP: 正解の異常区間のうち、区間内に 1 点以上の検知があったもの（区間数）
    - FN: 検知が 1 点も無かった正解区間（区間数）
    - FP: 正解区間の外にある検知点を、連続していれば 1 件にまとめた「誤検知イベント」数
      （点数で数えると「広く塗る」方式が過度に罰されるため、イベント単位で数える）

    Returns: dict(precision, recall, f1, tp, fp, fn)
    """
    pred = list(bool(x) for x in pred_flags)

    # TP / FN: 正解区間ごとに検知の有無を見る
    tp = 0
    for s, e in gt_windows:
        if any(pred[i] for i, t in enumerate(timestamps) if s <= t <= e):
            tp += 1
    fn = len(gt_windows) - tp

    # FP: 正解区間外の検知点を、連続していれば 1 イベントとしてまとめる
    in_gt = [any(s <= t <= e for s, e in gt_windows) for t in timestamps]
    fp, prev_is_fp = 0, False
    for i, p in enumerate(pred):
        cur_is_fp = p and not in_gt[i]
        if cur_is_fp and not prev_is_fp:
            fp += 1
        prev_is_fp = cur_is_fp

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    # 誤検知の「点数」と「率」。点数は系列長・間引き設定に依存して比較できないため、
    # 正常点（正解区間の外）あたりの率に正規化した false_alarm_rate を主に使う。
    false_alarm_points = sum(1 for i, p in enumerate(pred) if p and not in_gt[i])
    normal_points = sum(1 for g in in_gt if not g)
    far = false_alarm_points / normal_points if normal_points else float("nan")
    return {
        "windows_total": len(gt_windows),
        "window_recall": round(recall, 3),  # 異常区間の検出率（= recall）
        "precision": round(precision, 3),
        "f1": round(f1, 3),
        "tp": tp,
        "fp": fp,  # 誤検知イベント数（連続する誤検知点を 1 件にまとめたもの）
        "fn": fn,
        "false_alarm_rate": round(far, 4),  # 誤検知率 = 誤検知点 / 正常点
        "false_alarms": false_alarm_points,  # 誤検知点数（参考。間引き設定で変わるので比較不可）
        "n_pred": sum(1 for p in pred if p),
    }


def save_plot(series, timestamps, pred_flags, gt_windows, path, title=""):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(timestamps, series, color="#1f77b4", lw=0.8, label="sensor value")
    for i, (s, e) in enumerate(gt_windows):
        ax.axvspan(s, e, color="#ff7f0e", alpha=0.12, label="labeled anomaly window" if i == 0 else None)
    idx = [i for i, f in enumerate(pred_flags) if f]
    if idx:
        ax.scatter([timestamps[i] for i in idx], [series[i] for i in idx], color="#d62728", s=12, zorder=5, label="detected anomaly")
    ax.set_xlabel("time")
    ax.set_ylabel("value")
    if title:
        ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"[plot] saved: {path}")
