import argparse
import csv
import json
import os
import urllib.request
from datetime import datetime

import numpy as np
import pandas as pd
import yaml
from openai import OpenAI
from tsfm_public.models.tspulse.modeling_tspulse import TSPulseForReconstruction
from tsfm_public.toolkit.ad_helpers import AnomalyScoreMethods
from tsfm_public.toolkit.time_series_anomaly_detection_pipeline import TimeSeriesAnomalyDetectionPipeline

PROMPTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.yaml")


# =============================================================================
# 時系列センサーデータの異常検知 → 自然言語レポート化（TSFM + LLM の 2 段構成）
#
#   [検知層] TSPulse（IBM の時系列基盤モデル / TSFM。異常検知を公式サポート）
#     - nlp_processing/67 が使う Chronos は「予測」モデルで、異常検知は予測残差の転用
#       だった。TSPulse は異常検知そのものを学習しており、公式パイプライン
#       (TimeSeriesAnomalyDetectionPipeline) が異常スコアと検知フラグを直接返す。
#     - 108 万パラメータと小さく CPU で動く。追加学習なし（ゼロショット）。
#   [説明層] OpenAI 互換 LLM（既定は Google Gemini）
#     - 検知された異常点の数値サマリだけを LLM に渡し、根本原因の仮説・推奨対応まで
#       日本語レポートとして生成させる（67 と同じ設計。生の時系列は渡さない）。
#
#   入力は実際のセンサーデータ（NAB）。--input で自前の 1 変量 CSV も使える。
# =============================================================================


# NAB（Numenta Anomaly Benchmark）の実センサーデータ。timestamp,value 形式・既知異常区間ラベル付き。
NAB_BASE = "https://raw.githubusercontent.com/numenta/NAB/master"
NAB_LABELS_URL = f"{NAB_BASE}/labels/combined_windows.json"
NAB_PRESETS = {
    "machine-temp": "realKnownCause/machine_temperature_system_failure.csv",  # 産業機械の温度センサー
    "ambient-temp": "realKnownCause/ambient_temperature_system_failure.csv",  # 室温センサー
    "cpu": "realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv",  # サーバ CPU 使用率
    "traffic-speed": "realTraffic/speed_7578.csv",  # 道路の車速センサー
    "traffic-occupancy": "realTraffic/occupancy_6005.csv",  # 道路の占有率センサー
    "network": "realAWSCloudwatch/ec2_network_in_5abac7.csv",  # サーバ受信ネットワーク量
}


def _download(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print(f"[download] {url} -> {path}")
        tmp = path + ".tmp"
        urllib.request.urlretrieve(url, tmp)
        os.replace(tmp, path)


def load_nab_dataset(key, data_dir="datasets/nab", downsample=1):
    """NAB の実センサーデータと既知異常区間ラベルをダウンロードして読み込む。

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
        next(reader)  # ヘッダ (timestamp,value)
        for row in reader:
            timestamps.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
            values.append(float(row[1]))

    if downsample > 1:
        timestamps, values = timestamps[::downsample], values[::downsample]

    with open(labels_path) as f:
        windows = json.load(f).get(nab_key, [])
    gt_windows = [(datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S"), datetime.strptime(e[:19], "%Y-%m-%d %H:%M:%S")) for s, e in windows]

    return np.asarray(values, dtype=np.float32), timestamps, gt_windows


# ---- 正解ラベルでの検知精度評価（3 系統 (a)/(b)/(c) と同一実装。nlp_processing/69 の nab_common.py と同じ）----
def gt_flags_from_windows(timestamps, gt_windows):
    """各点が既知異常区間内かどうかの正解ブールを返す。"""
    flags = np.zeros(len(timestamps), dtype=bool)
    for i, t in enumerate(timestamps):
        flags[i] = any(s <= t <= e for s, e in gt_windows)
    return flags


def evaluate(pred_flags, timestamps, gt_windows):
    """異常「区間」単位で Precision / Recall / F1 を算出する。

    本 Tip の検知はいずれも系列全体を一度に見るバッチ処理なので、
    検出の早さを評価する NAB 公式スコア（ストリーミング検出器向け）は前提が合わない。
    ここでは「異常区間をいくつ当てたか」「誤検知をいくつ出したか」を素直に測る。
    """
    pred = list(bool(x) for x in pred_flags)
    in_gt = [any(s <= t <= e for s, e in gt_windows) for t in timestamps]

    tp = 0
    for s, e in gt_windows:
        if any(pred[i] for i, t in enumerate(timestamps) if s <= t <= e):
            tp += 1
    fn = len(gt_windows) - tp

    # 誤検知イベント: 正解区間外の検知点を、連続していれば 1 件にまとめる
    fp, prev_is_fp = 0, False
    for i, p in enumerate(pred):
        cur_is_fp = p and not in_gt[i]
        if cur_is_fp and not prev_is_fp:
            fp += 1
        prev_is_fp = cur_is_fp

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    false_alarm_points = sum(1 for i, p in enumerate(pred) if p and not in_gt[i])
    normal_points = sum(1 for g in in_gt if not g)
    far = false_alarm_points / normal_points if normal_points else float("nan")
    return {
        "windows_total": len(gt_windows),
        "window_recall": round(recall, 3),
        "precision": round(precision, 3),
        "f1": round(f1, 3),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "false_alarm_rate": round(far, 4),
        "false_alarms": false_alarm_points,
        "n_pred": sum(1 for p in pred if p),
    }


def load_series_csv(path):
    """任意の CSV（ヘッダなし・数値のみ、複数列なら最終列）を 1 変量系列として読み込む。"""
    arr = np.loadtxt(path, delimiter=",", ndmin=2, comments="#")
    values = arr[:, -1].astype(np.float32)
    return values, list(range(len(values))), []


def detect_anomalies_tspulse(series, timestamps, model_id, prediction_modes, aggregation_length, smoothing_length, threshold):
    """TSPulse の公式異常検知パイプラインで異常スコアと検知フラグを得る。

    67 の Chronos 版と違い、**異常スコアの式を自作する必要がない**（TSPulse が
    anomaly_score を直接返す）。ただし「スコアのどこから異常とみなすか」の
    しきい値は利用者が決める（公式 notebook も anomaly_score > 0.6 としている）。

    Returns: scores(np.ndarray), flags(np.ndarray[bool])
    """
    model = TSPulseForReconstruction.from_pretrained(
        model_id,
        num_input_channels=1,
        revision="main",  # 異常検知は main リビジョンを使う（公式 notebook 準拠）
        mask_type="user",
    )
    pipeline = TimeSeriesAnomalyDetectionPipeline(
        model,
        timestamp_column="timestamp",
        target_columns=["value"],
        prediction_mode=prediction_modes,
        aggregation_length=aggregation_length,
        aggr_function="max",
        smoothing_length=smoothing_length,
        least_significant_scale=0.01,
        least_significant_score=0.1,
    )
    df = pd.DataFrame({"timestamp": timestamps, "value": series})
    # パイプラインが返すのは timestamp / value / anomaly_score の 3 列（検知フラグは含まれない）
    result = pipeline(df, batch_size=256, predictive_score_smoothing=False)
    scores = result["anomaly_score"].to_numpy(dtype=np.float32)
    flags = scores > threshold
    return scores, flags


def build_anomaly_summary(series, timestamps, scores, flags, top_k=15):
    """LLM に渡す異常点の要約テキストを組み立てる（多すぎる場合はスコア上位のみ）。

    67 と同じく「検証可能な事実」だけを渡す。ここでは実測値と異常スコアに加え、
    系列全体の中央値を基準として添え、LLM が値の高低を判断できるようにする。
    """
    idx = [i for i, f in enumerate(flags) if f]
    med = float(np.median(series))
    lines = [
        f"系列長: {len(series)} 点 / 検知された異常点数: {len(idx)} / 系列全体の中央値: {med:.2f}",
    ]
    shown = sorted(idx, key=lambda i: scores[i], reverse=True)[:top_k]
    lines.append(f"異常スコア上位 {len(shown)} 点（時刻, 実測値, 中央値との差, 異常スコア）:")
    for i in sorted(shown):
        lines.append(f"- {timestamps[i]}: 実測={series[i]:.2f}, 中央値との差={series[i] - med:+.2f}, 異常スコア={scores[i]:.3f}")
    return "\n".join(lines)


def generate_report_llm(summary, data_label, base_url, model, api_key, max_tokens, reasoning_effort=None):
    """異常点の要約を LLM に渡し、自然言語の異常レポートを生成する（プロンプトは prompts.yaml）。"""
    with open(PROMPTS_PATH) as f:
        prompts = yaml.safe_load(f)
    user = prompts["user_template"].format(summary=summary, data_label=data_label)

    kwargs = {}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if reasoning_effort:
        kwargs["reasoning_effort"] = reasoning_effort

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompts["system"]}, {"role": "user", "content": user}],
        temperature=0.0,  # 事実に忠実なレポートを狙い決定的に生成する
        **kwargs,
    )
    return resp.choices[0].message.content or ""


def save_plot(series, timestamps, flags, gt_windows, path, title=""):
    """センサー値・正解ラベル・検知結果を 1 枚に重ねて保存する。"""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(timestamps, series, color="#1f77b4", lw=0.8, label="sensor value")
    for i, (s, e) in enumerate(gt_windows):
        ax.axvspan(s, e, color="#ff7f0e", alpha=0.12, label="labeled anomaly window" if i == 0 else None)
    idx = [i for i, f in enumerate(flags) if f]
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", type=str, default="ibm-granite/granite-timeseries-tspulse-r1", help="検知層の TSFM（TSPulse）")
    parser.add_argument("--nab-key", type=str, default="machine-temp", help="NAB データ選択。プリセット: " + ", ".join(NAB_PRESETS))
    parser.add_argument("--input", type=str, default=None, help="自前の 1 変量 CSV（ヘッダなし・数値のみ）")
    # TSPulse の異常検知はベースコンテキスト長(512)の 3〜4 倍（約 1536〜2048 点）以上を要求するため、既定は間引きなし
    parser.add_argument("--downsample", type=int, default=1, help="間引き間隔（既定 1 = 間引きなし。TSPulse は長い系列を要求する）")
    parser.add_argument(
        "--prediction-mode",
        type=str,
        nargs="+",
        default=[AnomalyScoreMethods.TIME_RECONSTRUCTION.value, AnomalyScoreMethods.FREQUENCY_RECONSTRUCTION.value],
        help="異常スコアの算出モード（time / fft / forecast / meandev / probabilistic）",
    )
    parser.add_argument("--aggregation-length", type=int, default=64, help="スコア集約の窓長")
    parser.add_argument("--smoothing-length", type=int, default=8, help="スコアの平滑化窓長")
    # 公式 notebook は anomaly_score > 0.6 を採用している。TSPulse のスコアは 0〜1 に正規化されるため、
    # Chronos（67）のようにセンサーごとに桁違いの調整をする必要はないが、しきい値自体は利用者が決める。
    parser.add_argument("--threshold", type=float, default=0.6, help="異常とみなす anomaly_score のしきい値（公式 notebook 準拠）")
    parser.add_argument("--plot", type=str, default=None)
    parser.add_argument("--report-out", type=str, default=None)
    parser.add_argument("--base-url", type=str, default="https://generativelanguage.googleapis.com/v1beta/openai/")
    parser.add_argument("--llm-model", type=str, default="gemini-3.5-flash")
    parser.add_argument("--max-tokens", type=int, default=None, help="生成トークン上限。未指定ならプロバイダ側の上限まで生成（推奨）")
    parser.add_argument("--reasoning-effort", type=str, default="low", choices=["low", "medium", "high"])
    args = parser.parse_args()

    # 1. 時系列を用意する
    if args.input:
        series, timestamps, gt_windows = load_series_csv(args.input)
        label = args.input
        stem = os.path.splitext(os.path.basename(args.input))[0]
        print(f"[data] CSV: {args.input}（{len(series)} 点）")
    else:
        series, timestamps, gt_windows = load_nab_dataset(args.nab_key, downsample=args.downsample)
        label = f"NAB: {NAB_PRESETS.get(args.nab_key, args.nab_key)}"
        stem = args.nab_key if args.nab_key in NAB_PRESETS else os.path.splitext(os.path.basename(args.nab_key))[0]
        print(f"[data] {label}（{len(series)} 点, 既知異常区間 {len(gt_windows)} 個）")

    plot_path = args.plot or f"images/{stem}_anomaly.png"
    report_path = args.report_out or f"reports/{stem}.md"

    # 2. 検知層: TSPulse の公式パイプラインで異常検知
    scores, flags = detect_anomalies_tspulse(
        series,
        timestamps,
        args.model_id,
        args.prediction_mode,
        args.aggregation_length,
        args.smoothing_length,
        args.threshold,
    )
    summary = build_anomaly_summary(series, timestamps, scores, flags)
    print("\n===== 検知結果（TSPulse）=====")
    print(summary)

    metrics = None
    if gt_windows:
        metrics = evaluate(flags, timestamps, gt_windows)
        print(f"[eval] {metrics}")

    save_plot(series, timestamps, flags, gt_windows, plot_path, title="TSPulse (anomaly-detection TSFM)")

    # 3. 説明層: LLM が自然言語レポート化（異常が無ければスキップ）
    report = ""
    if int(flags.sum()) > 0:
        api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
        try:
            report = generate_report_llm(summary, label, args.base_url, args.llm_model, api_key, args.max_tokens, args.reasoning_effort)
            print("\n===== 自然言語レポート（LLM）=====")
            print(report)
        except Exception as e:
            print(f"[warn] レポート生成に失敗: {e}")

    os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
    with open(report_path, "w") as f:
        f.write(f"# 異常検知レポート\n\n- データ: {label}\n- 検知モデル: {args.model_id}\n")
        if metrics:
            f.write(f"- 評価（NAB 既知異常区間ラベル基準）: {metrics}\n")
        f.write("\n")
        f.write(f"## 検知結果（TSPulse）\n\n```\n{summary}\n```\n\n")
        if report:
            f.write(f"## 自然言語レポート（LLM: {args.llm_model}）\n\n{report}\n")
    print(f"[report] saved: {report_path}")
