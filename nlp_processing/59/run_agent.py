import argparse

import dspy


# =============================================================================
# ツール（エージェントが呼び出せる外部機能）
#   ReAct エージェントは「どのツールをどの引数で呼ぶか」を LLM 自身に判断させる。
#   そのため各ツールには docstring（機能説明）と型ヒントが必須で、DSPy はこれを
#   読み取ってツールのスキーマ（名前・説明・引数）を LLM に提示する。
# =============================================================================

# 人口のローカル DB（API キー不要でオフライン実行できるよう、辞書で代用）
_POPULATION = {
    "日本": 124_000_000,
    "アメリカ": 335_000_000,
    "中国": 1_410_000_000,
    "インド": 1_430_000_000,
    "ドイツ": 84_000_000,
}


def get_population(country: str) -> int:
    """指定された国の人口（人数）を返す。

    Args:
        country: 日本語の国名（例: "日本", "ドイツ"）。
    """
    return _POPULATION.get(country.strip(), -1)


def calculator(expression: str) -> float:
    """四則演算の式を評価して数値の結果を返す。

    Args:
        expression: + - * / ( ) と数字からなる式（例: "(124000000 + 84000000) / 2"）。
    """
    # 安全のため組み込み関数を一切渡さずに評価する（任意コード実行を防ぐ）
    return eval(expression, {"__builtins__": {}}, {})


# =============================================================================
# シグネチャ（エージェントの入出力契約 ＝ プロンプトを文字列ではなく型で宣言する）
# =============================================================================
class AgentTask(dspy.Signature):
    """あなたは有能なエージェントです。利用可能なツールを使って、ユーザーの質問に具体的な数値で答えてください。"""
    question: str = dspy.InputField()
    answer: str = dspy.OutputField(desc="最終的な答え（具体的な数値）。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="qwen3.5:4b",
                        help="ツール呼び出しを行う Ollama モデル（小さすぎるとツール選択を誤りやすい）")
    parser.add_argument("--question", type=str,
                        default="日本とドイツの人口の合計を 2 で割るといくつ？",
                        help="エージェントへの質問")
    parser.add_argument("--max-iters", type=int, default=6,
                        help="ReAct ループ（Thought→Action→Observation）の最大反復回数")
    args = parser.parse_args()

    # Ollama 上のローカル LLM を DSPy（LiteLLM 経由）で使う。think=False で Qwen3.5 の
    # 思考モードを無効化（CPU では思考生成だけで激遅になるため）
    lm = dspy.LM(f"ollama_chat/{args.model}", api_base="http://localhost:11434",
                 api_key="", temperature=0.0, max_tokens=1024, think=False)
    dspy.configure(lm=lm)

    # ReAct エージェントを構築。tools には通常の Python 関数をそのまま渡せる
    # （DSPy が docstring と型ヒントからツールスキーマを生成し、内部に finish ツールを自動追加する）
    agent = dspy.ReAct(AgentTask, tools=[get_population, calculator], max_iters=args.max_iters)

    pred = agent(question=args.question)

    # 思考・ツール呼び出し・観察の履歴（trajectory）を表示する
    print("=" * 60)
    print(f"Q: {args.question}\n")
    for k, v in pred.trajectory.items():
        print(f"{k}: {v}")
    print("=" * 60)
    print(f"A: {pred.answer}")
