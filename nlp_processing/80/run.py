"""Gemini Decisions API に問い合わせを判定させる。"""

import argparse
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MODEL = "gemini-decision-1"
SAMPLE_MESSAGE = "有料プランを解約したはずですが、今月も請求されました。返金を希望します。"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", default=os.getenv("DECISION_MESSAGE") or SAMPLE_MESSAGE)
    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        parser.error("GEMINI_API_KEY を設定してください")

    payload = {
        "model": MODEL,
        "input": args.message,
        "questions": {
            "refund_requested": {
                "type": "noul",
                "instructions": "問い合わせの送信者は返金を希望しているか。",
            },
            "department": {
                "type": "choice",
                "instructions": "問い合わせの主な要件を扱う部署はどれか。",
                "criteria": {
                    "billing": "請求、支払い、返金",
                    "technical": "障害や機能の不具合",
                    "account": "登録内容やログイン方法",
                },
            },
            "urgency": {
                "type": "score",
                "instructions": "問い合わせに明記された事実から緊急度を評価する。",
                "criteria": [
                    "通常。今すぐ対応が必要な事情は記載されていない",
                    "優先。期限が迫っている、または業務が止まっている",
                    "至急。不正利用など被害が進行している",
                ],
            },
        },
    }
    base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com")
    request = Request(
        f"{base_url.rstrip('/')}/v1beta/decisions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
    )
    try:
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
    except HTTPError as error:
        raise SystemExit(f"Gemini Decisions API: HTTP {error.code}") from None
    except (URLError, TimeoutError):
        raise SystemExit("Gemini Decisions API に接続できないか、応答がタイムアウトしました") from None
    except ValueError:
        raise SystemExit("Gemini Decisions API の応答を JSON として読み取れませんでした") from None

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
