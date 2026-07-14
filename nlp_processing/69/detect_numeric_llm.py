import argparse
import json
import os
import re

import numpy as np
import yaml
from openai import OpenAI

import nab_common as nab

PROMPTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.yaml")


# =============================================================================
# 系統 (a) 数値直接入力（SigLLM / LLMAD / LLMTime 系）
#   センサー時系列の数値をそのままテキスト化して LLM に渡し、異常点の index を
#   ゼロショットで返させる。検知精度を NAB の既知異常区間ラベルで評価する。
#   （検知を LLM 自身が行う点が、系統 (c) の「TSFM で検知」と異なる）
# =============================================================================


def detect_numeric_llm(series, timestamps, data_label, base_url, model, api_key, reasoning_effort):
    prompts = yaml.safe_load(open(PROMPTS_PATH))
    lines = "\n".join(f"{i},{timestamps[i]:%Y-%m-%d %H:%M},{series[i]:.2f}" for i in range(len(series)))
    user = prompts["detect_user_template"].format(data_label=data_label, n=len(series), series_text=lines)
    kwargs = {"reasoning_effort": reasoning_effort} if reasoning_effort else {}

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompts["detect_system"]},
                  {"role": "user", "content": user}],
        temperature=0.0, **kwargs,
    )
    content = (resp.choices[0].message.content or "").strip()
    content = re.sub(r"^```(?:json)?|```$", "", content, flags=re.M).strip()
    try:
        items = json.loads(content)
    except json.JSONDecodeError:
        items = []
    flags = np.zeros(len(series), dtype=bool)
    for it in items:
        i = it.get("index")
        if isinstance(i, int) and 0 <= i < len(series):
            flags[i] = True
    return flags, items


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--nab-key", type=str, default="machine-temp")
    parser.add_argument("--downsample", type=int, default=24,
                        help="間引き間隔（LLM への入力を現実的なトークン数に抑える）")
    parser.add_argument("--base-url", type=str,
                        default="https://generativelanguage.googleapis.com/v1beta/openai/")
    parser.add_argument("--llm-model", type=str, default="gemini-3.5-flash")
    parser.add_argument("--reasoning-effort", type=str, default="low", choices=["low", "medium", "high"])
    args = parser.parse_args()

    series, timestamps, gt_windows = nab.load_nab_dataset(args.nab_key, downsample=args.downsample)
    label = f"NAB: {nab.NAB_PRESETS.get(args.nab_key, args.nab_key)}"
    print(f"[data] {label}（{len(series)} 点, 既知異常区間 {len(gt_windows)} 個）")

    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    flags, items = detect_numeric_llm(series, timestamps, label, args.base_url, args.llm_model,
                                      api_key, args.reasoning_effort)
    metrics = nab.evaluate(flags, timestamps, gt_windows)
    print(f"[detect] 系統(a) 数値直接入力: 異常 {int(flags.sum())} 点検出")
    print(f"[eval] {metrics}")

    nab.save_plot(series, timestamps, flags, gt_windows,
                  f"images/{args.nab_key}_numeric_llm.png", title="(a) numeric-input LLM")
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/{args.nab_key}.md", "w") as f:
        f.write(f"# 系統(a) 数値直接入力 検知レポート\n\n- データ: {label}（{len(series)} 点）\n")
        f.write(f"- 検知モデル: {args.llm_model}\n- 評価（NAB 既知異常区間ラベル基準）: {metrics}\n\n")
        f.write("## 検出した異常点\n\n")
        for it in items:
            i = it.get("index")
            if isinstance(i, int) and 0 <= i < len(series):
                f.write(f"- index={i} ({timestamps[i]:%Y-%m-%d %H:%M}, 値={series[i]:.2f}): {it.get('reason','')}\n")
    print(f"[report] saved: reports/{args.nab_key}.md")
