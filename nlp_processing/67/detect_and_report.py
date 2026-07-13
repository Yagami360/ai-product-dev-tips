import argparse
import os

import numpy as np
import torch
from chronos import BaseChronosPipeline
from openai import OpenAI


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
#   数値時系列の扱いに弱い LLM の代わりに TSFM が異常スコアリングを担い、
#   LLM は「説明・レポート生成」に専念する役割分担が要点（商用例: Datadog Toto + Bits AI SRE）。
# =============================================================================


def make_synthetic_series(n=480, seed=42):
    """日次周期＋ノイズのベース系列に、スパイク（点異常）とレベルシフト（区間異常）を注入する。"""
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    # 周期 96（例: 15 分間隔で 1 日）の季節性 + 緩やかなトレンド + ノイズ
    base = 20.0 + 5.0 * np.sin(2 * np.pi * t / 96) + 0.005 * t
    series = base + rng.normal(0, 0.4, size=n)

    injected = []
    # スパイク（点異常）: 単発の急上昇
    series[300] += 12.0
    injected.append(("spike", 300, 300))
    # レベルシフト（区間異常）: 一定区間だけベースラインが持ち上がる
    series[400:430] += 6.0
    injected.append(("level_shift", 400, 429))
    return series.astype(np.float32), injected


def load_series(path):
    """CSV（ヘッダなし・数値のみ、複数列なら最終列）を 1 変量系列として読み込む。"""
    arr = np.loadtxt(path, delimiter=",", ndmin=2, comments="#")
    return arr[:, -1].astype(np.float32)


def detect_anomalies_chronos(series, model_id, device, context_length, threshold):
    """Chronos-Bolt のスライディング窓 1 ステップ予測で各点の異常スコアを算出する。

    Returns: scores(len==n), lows, highs, meds（先頭 context_length 点は NaN / 0 埋め）
    """
    n = len(series)
    if n <= context_length:
        raise ValueError(
            f"系列長 {n} が context_length {context_length} 以下です。"
            f"より長い系列を使うか --context-length を小さくしてください。"
        )

    dtype = torch.float32 if device == "cpu" else torch.bfloat16
    pipeline = BaseChronosPipeline.from_pretrained(model_id, device_map=device, torch_dtype=dtype)
    # 各対象点 t（context_length <= t < n）について context = series[t-W:t] を作り、バッチ化して 1 回で推論
    contexts = [series[t - context_length:t] for t in range(context_length, n)]
    context_batch = torch.tensor(np.stack(contexts), dtype=torch.float32)

    # quantiles: (num_windows, prediction_length=1, num_quantiles=3), mean: (num_windows, 1)
    quantiles, _ = pipeline.predict_quantiles(
        context_batch, prediction_length=1, quantile_levels=[0.1, 0.5, 0.9]
    )
    q = quantiles[:, 0, :].float().cpu().numpy()  # (num_windows, 3)
    low, med, high = q[:, 0], q[:, 1], q[:, 2]

    scores = np.zeros(n, dtype=np.float32)
    lows = np.full(n, np.nan, dtype=np.float32)
    meds = np.full(n, np.nan, dtype=np.float32)
    highs = np.full(n, np.nan, dtype=np.float32)
    band = np.maximum(high - low, 1e-6)  # ゼロ割回避
    actual = series[context_length:n]
    # 予測区間の外に出た分を band 幅で正規化（区間内なら 0）
    dev = np.where(actual > high, (actual - high) / band,
                   np.where(actual < low, (low - actual) / band, 0.0))
    scores[context_length:n] = dev
    lows[context_length:n], meds[context_length:n], highs[context_length:n] = low, med, high

    anomalies = [
        {"index": int(i), "value": float(series[i]),
         "expected_low": float(lows[i]), "expected_med": float(meds[i]), "expected_high": float(highs[i]),
         "score": float(scores[i])}
        for i in range(context_length, n) if scores[i] > threshold
    ]
    return scores, lows, meds, highs, anomalies


def build_anomaly_summary(series, anomalies, threshold):
    """LLM に渡す異常区間の要約テキストを組み立てる。"""
    lines = [
        f"系列長: {len(series)} 点 / 検知しきい値(スコア): {threshold} / 検知された異常点数: {len(anomalies)}",
        "各異常点（index, 実測値, 期待中央値, 期待区間[q0.1,q0.9], 逸脱スコア）:",
    ]
    for a in anomalies:
        lines.append(
            f"- index={a['index']}: 実測={a['value']:.2f}, 期待中央={a['expected_med']:.2f}, "
            f"期待区間=[{a['expected_low']:.2f}, {a['expected_high']:.2f}], スコア={a['score']:.2f}"
        )
    return "\n".join(lines)


def generate_report_llm(summary, base_url, model, api_key, max_tokens):
    """異常区間の要約を LLM に渡し、自然言語の異常レポートを生成する。"""
    client = OpenAI(api_key=api_key, base_url=base_url)
    system = (
        "あなたは IoT センサー/設備監視の運用アシスタントです。時系列異常検知エンジンが出力した"
        "異常区間の要約を受け取り、運用者向けの日本語レポートを作成します。"
    )
    user = (
        "以下は時系列基盤モデル（Chronos）が予測区間からの逸脱として検知した異常点の一覧です。\n\n"
        f"{summary}\n\n"
        "この情報だけを根拠に、次の構成でレポートを書いてください（推測は仮説と明記）:\n"
        "1. 異常の要約（何点・どの範囲で起きたか）\n"
        "2. 各異常の種別推定（スパイク/レベルシフト/季節性のずれ 等）と判断根拠\n"
        "3. 想定される根本原因の仮説\n"
        "4. 推奨される対応アクション"
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    # 一部の OpenAI 互換バックエンドは content=None を返すことがあるため空文字にフォールバック
    return resp.choices[0].message.content or ""


def save_plot(series, lows, highs, anomalies, path):
    """系列・予測区間・検知した異常点を可視化して PNG 保存する（任意）。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = np.arange(len(series))
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(t, series, color="#1f77b4", lw=1.0, label="sensor value")
    ax.fill_between(t, lows, highs, color="#1f77b4", alpha=0.15, label="Chronos [q0.1, q0.9]")
    if anomalies:
        idx = [a["index"] for a in anomalies]
        ax.scatter(idx, [series[i] for i in idx], color="#d62728", s=28, zorder=5, label="detected anomaly")
    ax.set_xlabel("time step")
    ax.set_ylabel("value")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    print(f"[plot] saved: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=str, default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("--model-id", type=str, default="amazon/chronos-bolt-base",
                        help="検知層の TSFM（Chronos-Bolt）")
    parser.add_argument("--input", type=str, default=None,
                        help="1 変量時系列の CSV パス。未指定なら合成データを使う")
    parser.add_argument("--context-length", type=int, default=96,
                        help="スライディング窓のコンテキスト長")
    parser.add_argument("--threshold", type=float, default=1.0,
                        help="異常判定スコアのしきい値（予測区間を band 幅の何倍外れたか）")
    parser.add_argument("--plot", type=str, default=None, help="可視化 PNG の保存先パス（任意）")
    # 説明層（OpenAI 互換 LLM）。既定はローカル Ollama。base_url 差し替えで任意の LLM を使える
    parser.add_argument("--no-llm", action="store_true", help="検知のみ行い LLM レポートを生成しない")
    parser.add_argument("--base-url", type=str, default="http://localhost:11434/v1")
    parser.add_argument("--llm-model", type=str, default="qwen3:4b")
    # reasoning 系モデル（Qwen3 等）は <think> で枠を消費するため、レポートが途切れないよう多めにとる
    parser.add_argument("--max-tokens", type=int, default=1500)
    args = parser.parse_args()

    # 1. 時系列を用意する（CSV or 合成データ）
    if args.input:
        series = load_series(args.input)
        injected = None
    else:
        series, injected = make_synthetic_series()
        print(f"[data] 合成データ（正解の注入異常: {injected}）")

    # 2. 検知層: Chronos-Bolt で異常スコアリング
    scores, lows, meds, highs, anomalies = detect_anomalies_chronos(
        series, args.model_id, args.device, args.context_length, args.threshold
    )
    summary = build_anomaly_summary(series, anomalies, args.threshold)
    print("\n===== 検知結果（Chronos-Bolt）=====")
    print(summary)

    if args.plot:
        save_plot(series, lows, highs, anomalies, args.plot)

    # 3. 説明層: LLM が自然言語レポート化
    if not args.no_llm and anomalies:
        api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")  # ローカル LLM は認証不要
        report = generate_report_llm(summary, args.base_url, args.llm_model, api_key, args.max_tokens)
        print("\n===== 自然言語レポート（LLM）=====")
        print(report)
