import argparse

from deepeval.models import OllamaModel
from deepeval.metrics import GEval, ArenaGEval
from deepeval.test_case import LLMTestCase, ArenaTestCase, Contestant, SingleTurnParams
from deepeval import compare


# =============================================================================
# 評価データ（ゴールデンタスク集）
#   各タスクは「質問」と「参照解答（ゴールデン）」、品質の異なる 2 つの候補回答
#   （good = 正しい / bad = 誤り・曖昧）を持つ。
#   いずれも自由形式の文章で表記が一意に定まらないため「完全一致採点」では測れない。
#   そこで DeepEval の LLM-as-judge メトリクスで採点する。
#   judge が good に高スコア・bad に低スコアを付けられれば、採点が機能していると言える。
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


def build_judge(model_name):
    """Ollama 上のローカル LLM を DeepEval の judge（評価モデル）として使う。
    temperature=0 で採点を決定的にする。API キー不要・GPU 不要で動く。"""
    return OllamaModel(model=model_name, base_url="http://localhost:11434", temperature=0)


def run_single(judge_model_name):
    """単一採点（GEval）: 1 つの回答を rubric で採点する DeepEval の LLM-as-judge メトリクス。
    参照解答（expected_output）を基準に正確性などを評価し、0.0〜1.0 のスコアと理由を返す。"""
    judge = build_judge(judge_model_name)
    metric = GEval(
        name="正確性",
        criteria=(
            "AI の回答（actual output）が、参照解答（expected output）に照らして正確・有用で"
            "簡潔かを評価する。回答の長さや言い回しではなく内容の正しさを最重視し、"
            "事実誤認や曖昧な回答は強く減点する。"
        ),
        # criteria に登場する入力・出力・参照解答を評価対象パラメータとして渡す
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
        model=judge,
    )

    print(f"=== 単一採点（DeepEval GEval, 0.0-1.0）  judge = {judge_model_name} ===")
    good_sum = bad_sum = 0.0
    for item in DATA:
        good_case = LLMTestCase(input=item["question"], actual_output=item["good"], expected_output=item["reference"])
        bad_case = LLMTestCase(input=item["question"], actual_output=item["bad"], expected_output=item["reference"])
        metric.measure(good_case)
        gs, gr = metric.score, metric.reason
        metric.measure(bad_case)
        bs, br = metric.score, metric.reason
        good_sum += gs
        bad_sum += bs
        print(f"\nQ: {item['question']}")
        print(f"  [良い回答] score={gs:.2f}  理由: {gr}")
        print(f"  [悪い回答] score={bs:.2f}  理由: {br}")
    n = len(DATA)
    print("\n" + "=" * 60)
    print(f"平均スコア: 良い回答 = {good_sum / n:.2f},  悪い回答 = {bad_sum / n:.2f}")
    print("→ judge が良い回答に高スコア・悪い回答に低スコアを付けられていれば採点が機能している")


def run_pairwise(judge_model_name):
    """ペア比較（ArenaGEval）: 2 つの回答を比較してより良い方を選ぶ DeepEval のメトリクス。
    ArenaGEval は内部で「ブラインド＋提示順シャッフル」を行い、位置バイアス・冗長性バイアスを抑制する
    （手動で順序を入れ替える必要がない）。compare() は {コンテスタント名: 勝利数} の辞書を返す。"""
    judge = build_judge(judge_model_name)
    metric = ArenaGEval(
        name="回答品質",
        criteria=(
            "質問（input）に対して、参照解答に照らしてより正確・有用で簡潔な回答（actual output）を"
            "返したコンテスタントを勝者に選ぶ。回答の提示順や長さに惑わされないこと。"
        ),
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        model=judge,
    )

    # 各問について「良い回答」「悪い回答」を 2 コンテスタントとして突き合わせる
    test_cases = [
        ArenaTestCase(contestants=[
            Contestant(name="良い回答", test_case=LLMTestCase(input=item["question"], actual_output=item["good"])),
            Contestant(name="悪い回答", test_case=LLMTestCase(input=item["question"], actual_output=item["bad"])),
        ])
        for item in DATA
    ]

    print(f"=== ペア比較（DeepEval ArenaGEval, 位置/冗長性バイアスは内部で抑制）  judge = {judge_model_name} ===")
    wins = compare(test_cases=test_cases, metric=metric)  # {"良い回答": 勝利数, "悪い回答": 勝利数}
    print("\n" + "=" * 60)
    print(f"勝利数: {wins}")
    print(f"→ 全 {len(DATA)} 問中、良い回答が {wins.get('良い回答', 0)} 勝できていれば judge が機能している")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge-model", type=str, default="qwen3.5:4b",
                        help="採点者（judge）に使う Ollama モデル。大きいほど人間との一致率が上がりやすい")
    parser.add_argument("--mode", type=str, default="single", choices=["single", "pairwise"],
                        help="single: GEval で単一採点（0-1） / pairwise: ArenaGEval でペア比較")
    args = parser.parse_args()

    if args.mode == "single":
        run_single(args.judge_model)
    else:
        run_pairwise(args.judge_model)
