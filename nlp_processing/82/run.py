"""AWS 上の Databricks の Unity Gateway 経由で Jev を呼び出す。"""

import argparse
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MODEL = "system.ai.typesafeai-jev-1-14-0"
SAMPLE_MESSAGE = "有料プランを解約したはずですが、今月も請求されました。返金を希望します。"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", default=os.getenv("DECISION_MESSAGE") or SAMPLE_MESSAGE)
    args = parser.parse_args()

    host = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")
    if not host or not token:
        parser.error("DATABRICKS_HOST と DATABRICKS_TOKEN を設定してください")

    payload = {
        "model": MODEL,
        "state": {"message": args.message},
        "questions": {
            "refund_requested": {
                "type": "noul",
                "instructions": "message の送信者は返金を希望しているか。",
            },
            "department": {
                "type": "choice",
                "instructions": "message の主な要件を扱う部署はどれか。",
                "criteria": {
                    "billing": "請求、支払い、返金",
                    "technical": "障害や機能の不具合",
                    "account": "登録内容やログイン方法",
                },
            },
            "urgency": {
                "type": "score",
                "instructions": "message に明記された事実から緊急度を評価する。",
                "criteria": [
                    "通常。今すぐ対応が必要な事情は記載されていない",
                    "優先。期限が迫っている、または業務が止まっている",
                    "至急。不正利用など被害が進行している",
                ],
            },
        },
    }
    request = Request(
        f"{host.rstrip('/')}/ai-gateway/typesafe/v1/systemone",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            result = json.load(response)
    except HTTPError as error:
        raise SystemExit(f"Databricks Unity Gateway: HTTP {error.code}") from None
    except (URLError, TimeoutError):
        raise SystemExit("Databricks Unity Gateway に接続できないか、応答がタイムアウトしました") from None
    except ValueError:
        raise SystemExit("Databricks Unity Gateway の応答を JSON として読み取れませんでした") from None

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
