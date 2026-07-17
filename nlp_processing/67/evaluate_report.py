import argparse
import json
import os
import re

import yaml
from openai import OpenAI

PROMPTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts.yaml")


# =============================================================================
# 生成した異常検知レポートの品質を LLM-as-judge で評価する。
#   reports/<センサー>.md（検知結果＋自然言語レポート）を入力に、忠実性・有用性・
#   可読性・フォーマット準拠を 1〜5 で採点する。judge プロンプトは prompts.yaml で管理。
# =============================================================================


def parse_report_file(path):
    """report.md から「検知結果（summary）」と「自然言語レポート（report）」を取り出す。"""
    text = open(path).read()
    m = re.search(r"## 検知結果.*?```(.*?)```", text, re.S)
    summary = m.group(1).strip() if m else ""
    m = re.search(r"## 自然言語レポート.*?\n(.*)$", text, re.S)
    report = m.group(1).strip() if m else ""
    return summary, report


def evaluate_report(summary, report, base_url, model, api_key, reasoning_effort=None):
    prompts = yaml.safe_load(open(PROMPTS_PATH))
    user = prompts["judge_user_template"].format(summary=summary, report=report)
    kwargs = {"reasoning_effort": reasoning_effort} if reasoning_effort else {}

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompts["judge_system"]}, {"role": "user", "content": user}],
        temperature=0.0,
        **kwargs,
    )
    content = (resp.choices[0].message.content or "").strip()
    content = re.sub(r"^```(?:json)?|```$", "", content, flags=re.M).strip()  # コードフェンス除去
    return json.loads(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=str, required=True, help="評価する report.md のパス")
    parser.add_argument("--base-url", type=str, default="https://generativelanguage.googleapis.com/v1beta/openai/")
    parser.add_argument("--judge-model", type=str, default="gemini-3.5-flash")
    parser.add_argument("--reasoning-effort", type=str, default="low", choices=["low", "medium", "high"])
    args = parser.parse_args()

    summary, report = parse_report_file(args.report)
    if not report:
        print(f"{args.report}: 自然言語レポートが無い（検知0件など）ため評価スキップ")
        raise SystemExit(0)

    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    scores = evaluate_report(summary, report, args.base_url, args.judge_model, api_key, args.reasoning_effort)
    print(f"=== 品質評価（judge: {args.judge_model}）: {args.report} ===")
    print(json.dumps(scores, ensure_ascii=False, indent=2))
