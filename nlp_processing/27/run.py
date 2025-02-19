import argparse
from deepeval import evaluate
import deepeval.metrics
from deepeval.metrics import HallucinationMetric
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evaluation_model', type=str, default="gpt-4o")
    parser.add_argument('--threshold', type=float, default=0.3)
    args = parser.parse_args()

    # テストケースの作成
    test_case = LLMTestCase(
        # LLM への入力文
        input="アインシュタインの相対性理論について説明してください",
        # LLM からの出力文（回答）
        actual_output="アインシュタインは特殊相対性理論と一般相対性理論を発表しました...",
        # RAG用データセットなどの引用元のコンテキストで、HallucinationMetric等では必須パラメータになる
        # CoherenceMetric（文章の一貫性を評価）等では、不要パラメータになる
        context=["アルベルト・アインシュタインは1905年に特殊相対性理論を、1915年に一般相対性理論を発表した..."]
    )

    # 品質評価指標の設定
    # HallucinationMetric: 大規模言語モデル（LLM）の出力に含まれる「ハルシネーション」—つまり与えられたコンテキストや事実に基づかない情報の生成—を検出し評価するための指標
    # G-EvalMetric: 汎用的な言語モデル評価指標
    # ...
    print("deepeval.metrics: ", dir(deepeval.metrics))

    metric = HallucinationMetric(
        model=args.evaluation_model,
        threshold=args.threshold,
        strict_mode=True,       # 厳格評価モード
        include_reason=True     # 理由の詳細を含める
    )
    # metric = GEval(
    #     model=args.evaluation_model,
    #     threshold=args.threshold,
    #     strict_mode=True,       # 厳格評価モード
    # )

    # 品質評価の実行
    try:
        result = evaluate([test_case], [metric])
        print(result)
    except Exception as e:
        print(e)
