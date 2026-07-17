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

from nab_score import nab_score


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
    """予測フラグを正解ラベルで公正に評価する。

    - window_recall: 既知異常区間のうち「区間内に予測点が1つ以上ある」割合（＝異常を見つけられたか）
    - false_alarms: 正解区間の外で異常と予測した点数（誤検知）
    - pa_f1: point-adjust F1（区間内に1点でも当たれば区間全点を検出扱い。TSAD の慣習指標。甘めなので注意）
    """
    gt = gt_flags_from_windows(timestamps, gt_windows)
    pred = np.asarray(pred_flags, dtype=bool)

    detected = sum(any(pred[i] for i, t in enumerate(timestamps) if s <= t <= e) for s, e in gt_windows)
    window_recall = detected / len(gt_windows) if gt_windows else float("nan")
    false_alarms = int(np.sum(pred & ~gt))

    # point-adjust: 検出された区間は全点 TP 扱い
    pa = pred.copy()
    for s, e in gt_windows:
        idx = [i for i, t in enumerate(timestamps) if s <= t <= e]
        if any(pred[i] for i in idx):
            for i in idx:
                pa[i] = True
    tp = int(np.sum(pa & gt))
    fp = int(np.sum(pa & ~gt))
    fn = int(np.sum(~pa & gt))
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    pa_f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {
        "windows_total": len(gt_windows),
        "windows_detected": detected,
        "window_recall": round(window_recall, 3),
        "false_alarms": false_alarms,
        "pa_f1": round(pa_f1, 3),
        "n_pred": int(np.sum(pred)),
        # NAB 公式スコア（0〜100・3 プロファイル）。上記の簡易指標と違い「検出の早さ」を
        # 評価し、誤検知にペナルティを課すため 0 未満（＝無検出より悪い）にもなり得る。
        "nab_official": nab_score(pred, timestamps, gt_windows),
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
