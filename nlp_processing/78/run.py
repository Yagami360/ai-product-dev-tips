"""saihai-v1-310m を CPU で使って問い合わせの担当部署を選ぶ。"""

import argparse
import json
import os

from transformers import AutoModel

MODEL = "hotchpotch/saihai-v1-310m"
REVISION = "704809fa038ff647b1a0e9cda963f1b8a06e0c95"
SAMPLE_MESSAGE = "有料プランを解約したはずですが、今月も請求されました。返金を希望します。"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", default=os.getenv("DECISION_MESSAGE") or SAMPLE_MESSAGE)
    args = parser.parse_args()

    model = AutoModel.from_pretrained(
        MODEL,
        revision=REVISION,
        trust_remote_code=True,
        device="cpu",
        attn_implementation="sdpa",
    )
    request = {
        "state": args.message,
        "questions": {
            "department": {
                "type": "choice",
                "instructions": "問い合わせの主な要件を扱う部署はどれか。",
                "criteria": {
                    "billing": "請求、支払い、返金",
                    "technical": "障害や機能の不具合",
                    "account": "登録内容やログイン方法",
                },
            },
        },
    }
    result = model.systemone(request, show_progress_bar=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
