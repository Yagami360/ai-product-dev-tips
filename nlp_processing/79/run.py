"""Jev でエージェントが参照するスキルを 1 件まで提案する。"""

import argparse
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MODEL = "jev-1.14.0"
SAMPLE_MESSAGE = "先月の請求書の内訳を確認したい"
CATALOG = {
    "billing_guide": {
        "summary": "請求書や支払い明細の確認",
        "details": "請求額の内訳、支払い履歴、明細の読み方を知りたい場合に使う。",
    },
    "troubleshooting_guide": {
        "summary": "画面や機能の不具合の調査",
        "details": "画面が表示されない、エラーが出る、既存の機能が使えない場合に使う。",
    },
    "usage_report_guide": {
        "summary": "利用状況の集計とレポートの作成",
        "details": "利用状況を期間ごとに集計、比較、出力する手順を知りたい場合に使う。",
    },
}
CASES = (
    (SAMPLE_MESSAGE, "billing_guide"),
    ("レポート作成画面が開かない", "troubleshooting_guide"),
    ("こんにちは。今日は何曜日？", None),
    ("請求の話もあります。何を相談するかまだ決めていません", None),
)


def threshold(value):
    number = float(value)
    if not 0 <= number <= 1:
        raise argparse.ArgumentTypeError("しきい値は 0 以上 1 以下にしてください")
    return number


def request_answers(base_url, api_key, state, questions):
    request = Request(
        f"{base_url.rstrip('/')}/v1/systemone",
        data=json.dumps(
            {"model": MODEL, "state": state, "questions": questions}, ensure_ascii=False
        ).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)["answers"]


def probability(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ValueError("確率が範囲外です")
    return value


def select_skill(message, catalog, query, min_fit, min_gap):
    if not catalog:
        return {"choice_only": None, "recommended": None, "fit": {}}

    candidates = list(catalog)
    first_choice = candidates[0]
    if len(candidates) > 1:
        ranking = query(
            {"message": message},
            {
                "rank": {
                    "type": "choice",
                    "instructions": "message の依頼に最も関連するガイドを選ぶ。",
                    "criteria": {skill_id: skill["summary"] for skill_id, skill in catalog.items()},
                }
            },
        )["rank"]
        first_choice = ranking["choice"]
        if first_choice not in catalog:
            raise ValueError("候補にないスキルです")
        probabilities = {
            skill_id: probability(ranking["probabilities"][skill_id]) for skill_id in candidates
        }
        candidates.sort(
            key=lambda skill_id: (probabilities[skill_id], skill_id == first_choice), reverse=True
        )
    shortlist = candidates[:3]

    answers = query(
        {"message": message, "guides": {skill_id: catalog[skill_id]["details"] for skill_id in shortlist}},
        {
            skill_id: {
                "type": "noul",
                "instructions": (
                    f"message に具体的な依頼があり、guides 内の {skill_id} が"
                    "その主な依頼に答えるために役立つか。"
                ),
            }
            for skill_id in shortlist
        },
    )
    fit = {skill_id: probability(answers[skill_id]["noul"]) for skill_id in shortlist}
    ranked = sorted(shortlist, key=fit.__getitem__, reverse=True)
    best = ranked[0]
    has_margin = len(ranked) == 1 or fit[best] - fit[ranked[1]] >= min_gap
    recommended = best if fit[best] >= min_fit and has_margin else None
    return {"choice_only": first_choice, "recommended": recommended, "fit": fit}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", default=os.getenv("DECISION_MESSAGE") or SAMPLE_MESSAGE)
    parser.add_argument("--min-fit", type=threshold, default=os.getenv("JEV_MIN_FIT", "0.70"))
    parser.add_argument("--min-gap", type=threshold, default=os.getenv("JEV_MIN_GAP", "0.15"))
    parser.add_argument("--evaluate", action="store_true", help="サンプル 4 件で 2 方式を比較する")
    args = parser.parse_args()

    api_key = os.getenv("TYPESAFE_API_KEY")
    if not api_key:
        parser.error("TYPESAFE_API_KEY を設定してください")
    base_url = os.getenv("TYPESAFE_BASE_URL", "https://api.typesafe.ai")

    def query(state, questions):
        return request_answers(base_url, api_key, state, questions)

    try:
        if args.evaluate:
            rows = []
            for message, expected in CASES:
                result = select_skill(message, CATALOG, query, args.min_fit, args.min_gap)
                rows.append({"message": message, "expected": expected, **result})
            result = {
                "cases": rows,
                "choice_only_correct": sum(row["choice_only"] == row["expected"] for row in rows),
                "two_stage_correct": sum(row["recommended"] == row["expected"] for row in rows),
                "total": len(rows),
            }
        else:
            result = select_skill(args.message, CATALOG, query, args.min_fit, args.min_gap)
    except HTTPError as error:
        raise SystemExit(f"Jev API: HTTP {error.code}") from None
    except (URLError, TimeoutError):
        raise SystemExit("Jev API に接続できないか、応答がタイムアウトしました") from None
    except (ValueError, TypeError, KeyError):
        raise SystemExit("Jev API の応答形式を確認してください") from None

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
