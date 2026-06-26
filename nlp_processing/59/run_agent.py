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
    "japan": 124_000_000,
    "usa": 335_000_000,
    "china": 1_410_000_000,
    "india": 1_430_000_000,
    "germany": 84_000_000,
}


def get_population(country: str) -> int:
    """Return the population (number of people) of the given country.

    Args:
        country: English country name, e.g. "Japan", "USA".
    """
    return _POPULATION.get(country.strip().lower(), -1)


def calculator(expression: str) -> float:
    """Evaluate a basic arithmetic expression and return the numeric result.

    Args:
        expression: A math expression using + - * / ( ) and numbers, e.g. "(124000000 + 84000000) / 2".
    """
    # 安全のため組み込み関数を一切渡さずに評価する（任意コード実行を防ぐ）
    return eval(expression, {"__builtins__": {}}, {})


# =============================================================================
# シグネチャ（エージェントの入出力契約 ＝ プロンプトを文字列ではなく型で宣言する）
# =============================================================================
class AgentTask(dspy.Signature):
    """You are a helpful agent. Use the available tools to answer the user's question with a concrete number."""
    question: str = dspy.InputField()
    answer: str = dspy.OutputField(desc="The final answer, as a concrete number.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="qwen3.5:4b",
                        help="ツール呼び出しを行う Ollama モデル（小さすぎるとツール選択を誤りやすい）")
    parser.add_argument("--question", type=str,
                        default="What is the combined population of Japan and Germany, divided by 2?",
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
