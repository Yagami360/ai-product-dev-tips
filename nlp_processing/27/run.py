import argparse
from deepeval import evaluate
from deepeval.metrics import HallucinationMetric
from deepeval.test_case import LLMTestCase


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', type=float, default=0.3)
    args = parser.parse_args()

    # テストケースの作成
    test_case = LLMTestCase(
        input="アインシュタインの相対性理論について説明してください",
        actual_output="アインシュタインは特殊相対性理論と一般相対性理論を発表しました...",
        context=["アルベルト・アインシュタインは1905年に特殊相対性理論を、1915年に一般相対性理論を発表した..."]
    )

    # 評価指標の設定
    metric = HallucinationMetric(threshold=args.threshold)

    # 評価の実行
    try:
        result = evaluate([test_case], [metric])
        print(result)
    except Exception as e:
        print(e)
