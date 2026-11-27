"""OpenAI Decisions API に問い合わせを判定させる。"""

import argparse
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MODEL = "gpt-6-luna"
SAMPLE_MESSAGE = "有料プランを解約したはずですが、今月も請求されました。返金を希望します。"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", default=os.getenv("DECISION_MESSAGE") or SAMPLE_MESSAGE)
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        parser.error("OPENAI_API_KEY を設定してください")

    payload = {
        "model": MODEL,
        "input": args.message,
        "questions": [
            {
                "type": "predicate",
                "name": "refund_requested",
                "instructions": "問い合わせの送信者は返金を希望しているか。",
            },
            {
                "type": "choice",
                "name": "department",
                "instructions": "問い合わせの主な要件を扱う部署はどれか。",
                "choices": [
                    {"value": "billing", "description": "請求、支払い、返金"},
                    {"value": "technical", "description": "障害や機能の不具合"},
                    {"value": "account", "description": "登録内容やログイン方法"},
                ],
            },
            {
                "type": "score",
                "name": "urgency",
                "instructions": "問い合わせに明記された事実から緊急度を評価する。",
                "levels": [
                    {"label": "通常", "description": "今すぐ対応が必要な事情は記載されていない"},
                    {"label": "優先", "description": "期限が迫っている、または業務が止まっている"},
                    {"label": "至急", "description": "不正利用など被害が進行している"},
                ],
            },
        ],
    }
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    request = Request(
        f"{base_url.rstrip('/')}/decisions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
    except HTTPError as error:
        raise SystemExit(f"OpenAI Decisions API: HTTP {error.code}") from None
    except (URLError, TimeoutError):
        raise SystemExit("OpenAI Decisions API に接続できないか、応答がタイムアウトしました") from None
    except ValueError:
        raise SystemExit("OpenAI Decisions API の応答を JSON として読み取れませんでした") from None

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
