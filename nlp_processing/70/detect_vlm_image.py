import argparse
import base64
import json
import os
import re
from datetime import datetime

import numpy as np
import yaml
from openai import OpenAI

import nab_common as nab

PROMPTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.yaml")


# =============================================================================
# 系統 (b) 画像化 → VLM（TAMA / AnomLLM 系）
#   センサー時系列を折れ線グラフ画像にして、マルチモーダル LLM(VLM) に「異常な時間帯」を
#   読み取らせる。VLM が返した時間帯を点フラグに変換し、NAB の既知異常区間ラベルで評価する。
# =============================================================================


def render_series_png(series, timestamps, path):
    """検知対象の生の折れ線グラフ（検知結果の重畳なし）を PNG に保存する。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.plot(timestamps, series, color="#1f77b4", lw=0.8)
    ax.set_xlabel("time"); ax.set_ylabel("value")
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)
    return path


def detect_vlm_image(series, timestamps, img_path, data_label, base_url, model, api_key, reasoning_effort):
    prompts = yaml.safe_load(open(PROMPTS_PATH))
    user_text = prompts["detect_user_template"].format(
        data_label=data_label, t_start=f"{timestamps[0]:%Y-%m-%d %H:%M}", t_end=f"{timestamps[-1]:%Y-%m-%d %H:%M}")
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    kwargs = {"reasoning_effort": reasoning_effort} if reasoning_effort else {}

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompts["detect_system"]},
            {"role": "user", "content": [
                {"type": "text", "text": user_text},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            ]},
        ],
        temperature=0.0, **kwargs,
    )
    content = (resp.choices[0].message.content or "").strip()
    content = re.sub(r"^```(?:json)?|```$", "", content, flags=re.M).strip()
    try:
        ranges = json.loads(content)
    except json.JSONDecodeError:
        ranges = []

    flags = np.zeros(len(series), dtype=bool)
    parsed = []
    for r in ranges:
        try:
            s = datetime.strptime(r["start"][:16], "%Y-%m-%d %H:%M")
            e = datetime.strptime(r["end"][:16], "%Y-%m-%d %H:%M")
        except (KeyError, ValueError, TypeError):
            continue
        parsed.append((s, e, r.get("reason", "")))
        for i, t in enumerate(timestamps):
            if s <= t <= e:
                flags[i] = True
    return flags, parsed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--nab-key", type=str, default="machine-temp")
    parser.add_argument("--downsample", type=int, default=24)
    parser.add_argument("--base-url", type=str,
                        default="https://generativelanguage.googleapis.com/v1beta/openai/")
    parser.add_argument("--llm-model", type=str, default="gemini-3.5-flash")
    parser.add_argument("--reasoning-effort", type=str, default="low", choices=["low", "medium", "high"])
    args = parser.parse_args()

    series, timestamps, gt_windows = nab.load_nab_dataset(args.nab_key, downsample=args.downsample)
    label = f"NAB: {nab.NAB_PRESETS.get(args.nab_key, args.nab_key)}"
    print(f"[data] {label}（{len(series)} 点, 既知異常区間 {len(gt_windows)} 個）")

    # 1. 検知対象の生グラフを画像化
    raw_png = render_series_png(series, timestamps, f"images/{args.nab_key}_input.png")

    # 2. VLM に画像を見せて異常な時間帯を検知
    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    flags, parsed = detect_vlm_image(series, timestamps, raw_png, label, args.base_url, args.llm_model,
                                     api_key, args.reasoning_effort)
    metrics = nab.evaluate(flags, timestamps, gt_windows)
    print(f"[detect] 系統(b) 画像化→VLM: 異常時間帯 {len(parsed)} 個 / 異常 {int(flags.sum())} 点")
    print(f"[eval] {metrics}")

    # 3. 検知結果を重畳した図と、レポートを保存
    nab.save_plot(series, timestamps, flags, gt_windows,
                  f"images/{args.nab_key}_vlm_image.png", title="(b) image -> VLM")
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/{args.nab_key}.md", "w") as f:
        f.write(f"# 系統(b) 画像化→VLM 検知レポート\n\n- データ: {label}（{len(series)} 点）\n")
        f.write(f"- 検知モデル(VLM): {args.llm_model}\n- 評価（NAB 既知異常区間ラベル基準）: {metrics}\n\n")
        f.write("## 検出した異常時間帯\n\n")
        for s, e, reason in parsed:
            f.write(f"- {s:%Y-%m-%d %H:%M} 〜 {e:%Y-%m-%d %H:%M}: {reason}\n")
    print(f"[report] saved: reports/{args.nab_key}.md")
