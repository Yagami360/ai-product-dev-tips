import re
import json
import argparse

import ollama


# =============================================================================
# 評価データ（ゴールデンタスク集）
#   各タスクは「質問」と「参照解答（ゴールデン）」、品質の異なる 2 つの候補回答
#   （good = 正しい / bad = 誤り・曖昧）を持つ。
#   いずれも自由形式の文章で、表記が一意に定まらないため「完全一致採点」では測れない。
#   そこで LLM 自身に rubric で採点させる（= LLM-as-judge）。
#   judge が good に高得点・bad に低得点を付けられれば、採点が機能していると言える。
# =============================================================================
DATA = [
    {
        "question": "光合成とは何か、簡潔に説明してください。",
        "reference": "植物などが光エネルギーを使い、二酸化炭素と水から酸素と糖（栄養）を作り出す反応。",
        "good": "光合成は、植物が光エネルギーを利用して二酸化炭素と水から酸素と糖を作り出す反応です。",
        "bad": "光合成とは、植物がごはんを食べて大きく育つことを指す言葉です。",
    },
    {
        "question": "HTTP の GET と POST の主な違いを説明してください。",
        "reference": "GET はデータ取得用で副作用がなくパラメータが URL に載る。POST はサーバーへデータを送信・更新する用途で、本体（body）にデータを載せる。",
        "good": "GET はサーバーからデータを取得する用途でパラメータを URL に付け、POST はデータを送信・更新する用途で本体（body）に載せます。",
        "bad": "GET と POST はどちらも同じもので、ページを開くときに好きな方を使えば違いはありません。",
    },
    {
        "question": "プログラミングにおける再帰関数とは何ですか。",
        "reference": "自分自身を呼び出す関数。終了条件（基底ケース）に達するまで、問題をより小さな同種の問題に分割しながら自分を呼び出す。",
        "good": "再帰関数とは自分自身を呼び出す関数で、基底ケース（終了条件）に達するまで問題を小さく分割しながら処理します。",
        "bad": "再帰関数とは、ループ処理を速くするために用意された特別な for 文のことです。",
    },
    {
        "question": "TCP と UDP の主な違いは何ですか。",
        "reference": "TCP は接続指向で再送・順序保証があり信頼性が高い。UDP はコネクションレスで保証がない代わりに低遅延・軽量。",
        "good": "TCP は接続を確立して再送や順序保証を行う信頼性重視のプロトコル、UDP は接続を張らず保証がない代わりに低遅延で軽量なプロトコルです。",
        "bad": "TCP は新しいプロトコルで高速、UDP は古いので現在はほとんど使われていません。",
    },
]


# rubric ベースの単一採点（MT-Bench の reference-guided single-answer grading）。
# 1 つの回答を参照解答を基準に 1〜10 で採点させる。
SINGLE_TEMPLATE = """あなたは公平で厳密な採点者です。以下の[質問]に対する[AI の回答]の品質を、[参照解答]を基準に評価してください。
評価観点は「正確性」「有用性」「簡潔さ」です。1（最低）〜10（最高）の整数で採点してください。
回答の長さや言い回しに惑わされず、内容が正しいかどうかを最重視してください。

[質問]
{question}

[参照解答]
{reference}

[AI の回答]
{answer}

出力は必ず次の JSON のみとし、他の文字は一切出力しないこと:
{{"score": <1〜10 の整数>, "reason": "<採点理由を 1 文で>"}}"""


# ペア比較（pairwise comparison）。2 つの回答のどちらが優れているかを判定させる。
PAIRWISE_TEMPLATE = """あなたは公平な審査員です。以下の[質問]に対する 2 つの回答[回答 A]と[回答 B]を比較し、どちらが優れているか判定してください。
[参照解答]を基準に「正確性」「有用性」「簡潔さ」で評価します。回答の提示順や長さに惑わされないでください。

[質問]
{question}

[参照解答]
{reference}

[回答 A]
{answer_a}

[回答 B]
{answer_b}

出力は必ず次の JSON のみとし、他の文字は一切出力しないこと:
{{"winner": "A" または "B" または "tie", "reason": "<判定理由を 1 文で>"}}"""


def chat_json(model, prompt):
    """Ollama 上の Qwen を JSON モードで呼び、辞書として返す。
    think=False で Qwen3.5 の思考生成を無効化（CPU では思考だけで激遅になるため）。"""
    resp = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        format="json",                                    # JSON 出力を強制
        options={"temperature": 0.0, "num_predict": 512},  # 採点は決定的にしたいので temperature=0
        think=False,
    )
    content = resp["message"]["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", content, re.DOTALL)       # 念のため最初の {...} を拾うフォールバック
        return json.loads(m.group(0)) if m else {}


def judge_single(model, item, answer):
    """1 つの回答を rubric で 1〜10 採点し、(score, reason) を返す。"""
    out = chat_json(model, SINGLE_TEMPLATE.format(
        question=item["question"], reference=item["reference"], answer=answer))
    score = int(out.get("score", 0))
    return max(1, min(10, score)), out.get("reason", "")


def judge_pairwise(model, item, answer_a, answer_b):
    """A/B を比較し 'A' / 'B' / 'TIE' を返す。"""
    out = chat_json(model, PAIRWISE_TEMPLATE.format(
        question=item["question"], reference=item["reference"],
        answer_a=answer_a, answer_b=answer_b))
    w = str(out.get("winner", "tie")).strip().upper()
    return w if w in ("A", "B") else "TIE"


def judge_pairwise_debiased(model, item):
    """位置バイアス対策つきのペア比較（MT-Bench 方式）。
    提示順を入れ替えて 2 回判定し、結論が一致したときだけその勝者を採用する。
    一致しなければ「順序に依存した判定（= 位置バイアス）」とみなして tie 扱いにする。"""
    # 順序1: A=good, B=bad
    pick1 = {"A": "good", "B": "bad", "TIE": "tie"}[judge_pairwise(model, item, item["good"], item["bad"])]
    # 順序2: A=bad, B=good（提示順を入れ替え）
    pick2 = {"A": "bad", "B": "good", "TIE": "tie"}[judge_pairwise(model, item, item["bad"], item["good"])]
    consistent = pick1 == pick2
    final = pick1 if consistent else "tie"
    return final, consistent, pick1, pick2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge-model", type=str, default="qwen3.5:4b",
                        help="採点者（judge）に使う Ollama モデル。大きいほど人間との一致率が上がりやすい")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "pairwise"],
                        help="single: rubric 単一採点（1-10） / pairwise: ペア比較（位置バイアス対策つき）")
    args = parser.parse_args()

    if args.mode == "single":
        print(f"=== 単一採点（rubric, 1-10）  judge = {args.judge_model} ===")
        good_sum = bad_sum = 0
        for item in DATA:
            gs, gr = judge_single(args.judge_model, item, item["good"])
            bs, br = judge_single(args.judge_model, item, item["bad"])
            good_sum += gs
            bad_sum += bs
            print(f"\nQ: {item['question']}")
            print(f"  [良い回答] score={gs:2d}  理由: {gr}")
            print(f"  [悪い回答] score={bs:2d}  理由: {br}")
        n = len(DATA)
        print("\n" + "=" * 60)
        print(f"平均スコア: 良い回答 = {good_sum / n:.1f} / 10,  悪い回答 = {bad_sum / n:.1f} / 10")
        print("→ judge が良い回答に高得点・悪い回答に低得点を付けられていれば採点が機能している")
    else:
        print(f"=== ペア比較（位置バイアス対策つき）  judge = {args.judge_model} ===")
        correct = flipped = 0
        for item in DATA:
            final, consistent, pick1, pick2 = judge_pairwise_debiased(args.judge_model, item)
            if not consistent:
                flipped += 1
            if final == "good":
                correct += 1
            flag = "順序で一致" if consistent else "順序で逆転（= 位置バイアス）→ tie"
            print(f"\nQ: {item['question']}")
            print(f"  順序1(A=良,B=悪)→{pick1} / 順序2(A=悪,B=良)→{pick2}  [{flag}]  最終: {final}")
        n = len(DATA)
        print("\n" + "=" * 60)
        print(f"良い回答を正しく勝たせた割合: {correct}/{n}")
        print(f"順序で結論が逆転した（位置バイアスを検出した）件数: {flipped}/{n}")
