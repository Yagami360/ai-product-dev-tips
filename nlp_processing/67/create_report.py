import argparse
import csv
import json
import os
import urllib.request
from datetime import datetime

import numpy as np
import torch
import yaml
from chronos import BaseChronosPipeline
from openai import OpenAI

PROMPTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.yaml")


# =============================================================================
# 時系列センサーデータの異常検知 → 自然言語レポート化（TSFM + LLM の 2 段構成）
#
#   [検知層] Chronos-Bolt（時系列基盤モデル / TSFM）
#     - スライディング窓で「次の 1 点」を確率予測（分位点 q0.1 / q0.5 / q0.9）し、
#       実測値が予測区間 [q0.1, q0.9] からどれだけ外れたか（band 幅で正規化）を
#       異常スコアとする。追加学習なし（ゼロショット）で動く。
#   [説明層] OpenAI 互換 LLM（既定はローカル Ollama + Qwen）
#     - 検知された異常区間の要約テキストを LLM に渡し、異常種別の推定・
#       根本原因の仮説・推奨対応までを日本語レポートとして生成させる。
#
#   入力は実際のセンサーデータ（NAB: 産業機械の温度センサー。既知の故障を含む）。
#   --input で自前の 1 変量 CSV も使える。
# =============================================================================


# NAB（Numenta Anomaly Benchmark）の実センサーデータ。timestamp,value 形式・既知異常区間ラベル付き。
# key は "<category>/<file>.csv"。温度以外（交通量・サーバ CPU 使用率など）も同形式で扱える。
NAB_BASE = "https://raw.githubusercontent.com/numenta/NAB/master"
NAB_LABELS_URL = f"{NAB_BASE}/labels/combined_windows.json"
NAB_PRESETS = {
    "machine-temp": "realKnownCause/machine_temperature_system_failure.csv",  # 産業機械の温度センサー
    "ambient-temp": "realKnownCause/ambient_temperature_system_failure.csv",  # 室温センサー
    "cpu": "realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv",                # サーバ CPU 使用率
    "traffic-speed": "realTraffic/speed_7578.csv",                            # 道路の車速センサー
    "traffic-occupancy": "realTraffic/occupancy_6005.csv",                    # 道路の占有率センサー
    "network": "realAWSCloudwatch/ec2_network_in_5abac7.csv",                 # サーバ受信ネットワーク量
}


def _download(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print(f"[download] {url} -> {path}")
        # 一時ファイルに落として原子的にリネーム（中断で壊れたファイルがキャッシュされるのを防ぐ）
        tmp = path + ".tmp"
        urllib.request.urlretrieve(url, tmp)
        os.replace(tmp, path)


def load_nab_dataset(key, data_dir="data", downsample=1):
    """NAB の実センサーデータと既知異常区間ラベルをダウンロードして読み込む。

    key は NAB_PRESETS のキー、または "<category>/<file>.csv" 形式の生キー。
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

    if downsample > 1:  # CPU 実行を軽くするための間引き（既定は間引きなし）
        timestamps, values = timestamps[::downsample], values[::downsample]

    with open(labels_path) as f:
        windows = json.load(f).get(nab_key, [])
    gt_windows = [(datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S"),
                   datetime.strptime(e[:19], "%Y-%m-%d %H:%M:%S")) for s, e in windows]

    return np.asarray(values, dtype=np.float32), timestamps, gt_windows


def load_series_csv(path):
    """任意の CSV（ヘッダなし・数値のみ、複数列なら最終列）を 1 変量系列として読み込む。"""
    arr = np.loadtxt(path, delimiter=",", ndmin=2, comments="#")
    values = arr[:, -1].astype(np.float32)
    return values, list(range(len(values))), []


def detect_anomalies_chronos(series, xs, model_id, device, context_length, threshold, batch_size):
    """Chronos-Bolt のスライディング窓 1 ステップ予測で各点の異常スコアを算出する。

    xs は各点の x 値（実データでは timestamp、それ以外は index）。
    Returns: scores, lows, meds, highs, anomalies
    """
    n = len(series)
    if n <= context_length:
        raise ValueError(
            f"系列長 {n} が context_length {context_length} 以下です。"
            f"より長い系列を使うか --context-length を小さくしてください。"
        )

    dtype = torch.float32 if device == "cpu" else torch.bfloat16
    pipeline = BaseChronosPipeline.from_pretrained(model_id, device_map=device, torch_dtype=dtype)

    # 各対象点 t（context_length <= t < n）について context = series[t-W:t] を作る
    contexts = [series[t - context_length:t] for t in range(context_length, n)]

    # 長い系列でもメモリを抑えるため、predict_quantiles をミニバッチに分けて呼ぶ
    q_list = []
    for i in range(0, len(contexts), batch_size):
        batch = torch.tensor(np.stack(contexts[i:i + batch_size]), dtype=torch.float32)
        quantiles, _ = pipeline.predict_quantiles(
            batch, prediction_length=1, quantile_levels=[0.1, 0.5, 0.9]
        )
        q_list.append(quantiles[:, 0, :].float().cpu().numpy())  # (b, 3)
        print(f"[detect] {min(i + batch_size, len(contexts))}/{len(contexts)} 窓を推論", end="\r")
    print()
    q = np.concatenate(q_list, axis=0)  # (num_windows, 3)
    low, med, high = q[:, 0], q[:, 1], q[:, 2]

    scores = np.zeros(n, dtype=np.float32)
    lows = np.full(n, np.nan, dtype=np.float32)
    meds = np.full(n, np.nan, dtype=np.float32)
    highs = np.full(n, np.nan, dtype=np.float32)
    band = np.maximum(high - low, 1e-6)  # ゼロ割回避
    actual = series[context_length:n]
    dev = np.where(actual > high, (actual - high) / band,
                   np.where(actual < low, (low - actual) / band, 0.0))
    scores[context_length:n] = dev
    lows[context_length:n], meds[context_length:n], highs[context_length:n] = low, med, high

    anomalies = [
        {"index": int(i), "x": str(xs[i]), "value": float(series[i]),
         "expected_low": float(lows[i]), "expected_med": float(meds[i]),
         "expected_high": float(highs[i]), "score": float(scores[i])}
        for i in range(context_length, n) if scores[i] > threshold
    ]
    return scores, lows, meds, highs, anomalies


def build_anomaly_summary(series, anomalies, threshold, top_k=15):
    """LLM に渡す異常区間の要約テキストを組み立てる（多すぎる場合はスコア上位のみ）。"""
    lines = [
        f"系列長: {len(series)} 点 / 検知しきい値(スコア): {threshold} / 検知された異常点数: {len(anomalies)}",
    ]
    shown = sorted(anomalies, key=lambda a: a["score"], reverse=True)[:top_k]
    lines.append(f"逸脱スコア上位 {len(shown)} 点（時刻, 実測値, 期待中央値, 期待区間[q0.1,q0.9], スコア）:")
    for a in sorted(shown, key=lambda a: a["index"]):
        lines.append(
            f"- {a['x']}: 実測={a['value']:.2f}, 期待中央={a['expected_med']:.2f}, "
            f"期待区間=[{a['expected_low']:.2f}, {a['expected_high']:.2f}], スコア={a['score']:.2f}"
        )
    return "\n".join(lines)


def generate_report_llm(summary, data_label, base_url, model, api_key, max_tokens, reasoning_effort=None):
    """異常区間の要約を LLM に渡し、自然言語の異常レポートを生成する。

    system / user プロンプトは prompts.yaml から読み込む（コードから分離して管理）。
    reasoning 系モデル（Gemini 3.x / Qwen3 等）は思考でトークンを消費するため、
    --reasoning-effort low を渡すと本文が途中で切れにくい（対応する OpenAI 互換 API のみ）。
    """
    with open(PROMPTS_PATH) as f:
        prompts = yaml.safe_load(f)
    system = prompts["system"]
    user = prompts["user_template"].format(summary=summary, data_label=data_label)

    # max_tokens は既定で送らない（送るとレポートが途中で切れやすい。未指定なら
    # プロバイダ側の上限まで生成させる）。reasoning_effort は対応 API のみ。
    kwargs = {}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if reasoning_effort:
        kwargs["reasoning_effort"] = reasoning_effort

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.3,
        **kwargs,
    )
    # 一部の OpenAI 互換バックエンドは content=None を返すため空文字にフォールバック
    return resp.choices[0].message.content or ""


def save_plot(series, xs, lows, highs, anomalies, gt_windows, path):
    """系列・予測区間・既知異常区間・検知した異常点を可視化して PNG 保存する。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(xs, series, color="#1f77b4", lw=0.8, label="sensor value")
    ax.fill_between(xs, lows, highs, color="#1f77b4", alpha=0.15, label="Chronos [q0.1, q0.9]")
    # 既知の異常区間（正解ラベル）を薄い帯で表示
    for i, (s, e) in enumerate(gt_windows):
        ax.axvspan(s, e, color="#ff7f0e", alpha=0.12, label="labeled anomaly window" if i == 0 else None)
    if anomalies:
        idx = [a["index"] for a in anomalies]
        ax.scatter([xs[i] for i in idx], [series[i] for i in idx],
                   color="#d62728", s=10, zorder=5, label="detected anomaly")
    ax.set_xlabel("time")
    ax.set_ylabel("value")
    ax.legend(loc="upper right", fontsize=8)
    if xs and isinstance(xs[0], datetime):  # x が時刻のときだけ日付軸を整形（--input の整数 index では不要）
        fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    print(f"[plot] saved: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=str, default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--model-id", type=str, default="amazon/chronos-bolt-base",
                        help="検知層の TSFM（Chronos-Bolt）")
    # 入力: 既定は NAB の実センサーデータ（機械温度）。--nab-key で別のセンサー、--input で任意 CSV
    parser.add_argument("--nab-key", type=str, default="machine-temp",
                        help="NAB データ選択。プリセット: " + ", ".join(NAB_PRESETS)
                             + " または '<category>/<file>.csv' 形式の生キー")
    parser.add_argument("--input", type=str, default=None, help="1 変量時系列の CSV パス（指定時はこれを使う）")
    parser.add_argument("--downsample", type=int, default=6,
                        help="実データの間引き間隔（既定 6 = 5分値を30分値に。CPU を軽くする）")
    parser.add_argument("--context-length", type=int, default=96, help="スライディング窓のコンテキスト長")
    parser.add_argument("--threshold", type=float, default=1.5, help="異常判定スコアのしきい値")
    parser.add_argument("--batch-size", type=int, default=256, help="Chronos 推論のミニバッチサイズ")
    parser.add_argument("--plot", type=str, default=None,
                        help="可視化 PNG の保存先（未指定なら images/<センサー>_anomaly.png）")
    parser.add_argument("--report-out", type=str, default=None,
                        help="検知結果＋レポートの保存先（未指定なら reports/<センサー>.md）")
    # 説明層（OpenAI 互換 LLM）。base_url 差し替えで任意の LLM を使える（既定は Gemini）
    parser.add_argument("--base-url", type=str,
                        default="https://generativelanguage.googleapis.com/v1beta/openai/")
    parser.add_argument("--llm-model", type=str, default="gemini-3.5-flash")
    # 既定では max_tokens を送らない（送るとレポートが途中で切れやすい）。必要時のみ上限指定
    parser.add_argument("--max-tokens", type=int, default=None,
                        help="生成トークン上限。未指定ならプロバイダ側の上限まで生成（推奨）")
    parser.add_argument("--reasoning-effort", type=str, default=None,
                        choices=["low", "medium", "high"],
                        help="reasoning 系モデルの思考量（対応 API のみ）。低くすると本文が切れにくい")
    args = parser.parse_args()

    # 1. 時系列を用意する（既定: NAB の実センサーデータ / --input で任意 CSV）
    if args.input:
        series, xs, gt_windows = load_series_csv(args.input)
        label = args.input
        stem = os.path.splitext(os.path.basename(args.input))[0]
        print(f"[data] CSV: {args.input}（{len(series)} 点）")
    else:
        series, xs, gt_windows = load_nab_dataset(args.nab_key, downsample=args.downsample)
        label = f"NAB: {NAB_PRESETS.get(args.nab_key, args.nab_key)}"
        stem = args.nab_key if args.nab_key in NAB_PRESETS else os.path.splitext(os.path.basename(args.nab_key))[0]
        print(f"[data] {label}（{len(series)} 点, 既知異常区間 {len(gt_windows)} 個）")

    # 出力ファイル名はセンサー名から自動導出（明示指定があればそれを優先）
    plot_path = args.plot or f"images/{stem}_anomaly.png"
    report_path = args.report_out or f"reports/{stem}.md"

    # 2. 検知層: Chronos-Bolt で異常スコアリング
    scores, lows, meds, highs, anomalies = detect_anomalies_chronos(
        series, xs, args.model_id, args.device, args.context_length, args.threshold, args.batch_size
    )
    summary = build_anomaly_summary(series, anomalies, args.threshold)
    print("\n===== 検知結果（Chronos-Bolt）=====")
    print(summary)

    save_plot(series, xs, lows, highs, anomalies, gt_windows, plot_path)

    # 3. 説明層: LLM が自然言語レポート化（異常が無ければスキップ）
    report = ""
    if anomalies:
        api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")  # ローカル LLM は認証不要
        try:
            report = generate_report_llm(summary, label, args.base_url, args.llm_model, api_key,
                                         args.max_tokens, args.reasoning_effort)
            print("\n===== 自然言語レポート（LLM）=====")
            print(report)
        except Exception as e:  # LLM 失敗時も検知結果は保存する（せっかくの検知結果を捨てない）
            print(f"\n[warn] LLM レポート生成に失敗: {e}\n検知結果のみ保存します。")

    # 4. 検知結果＋レポートを出力ファイル（Markdown）に保存
    os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
    with open(report_path, "w") as f:
        f.write(f"# 異常検知レポート\n\n- データ: {label}\n- 検知モデル: {args.model_id}\n\n")
        f.write(f"## 検知結果（Chronos-Bolt）\n\n```\n{summary}\n```\n\n")
        if report:
            f.write(f"## 自然言語レポート（LLM: {args.llm_model}）\n\n{report}\n")
    print(f"\n[report] saved: {report_path}")
