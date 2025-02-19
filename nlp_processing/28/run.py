import argparse
from deepeval.dataset import EvaluationDataset
from deepeval import evaluate
import deepeval.metrics
from deepeval.metrics import AnswerRelevancyMetric, SummarizationMetric
from deepeval.test_case import LLMTestCase


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', type=str, default="dataset_name")
    parser.add_argument('--evaluation_model', type=str, default="gpt-4o")
    parser.add_argument('--threshold', type=float, default=0.1)
    args = parser.parse_args()

    # DeepEval 上のデータセット
    dataset = EvaluationDataset()
    dataset.pull(alias=args.dataset_name)
    # print("dataset:", dataset)
    # print("dataset.goldens:", dataset.goldens)
    # print("dataset.test_cases:", dataset.test_cases)

    # データセットの各アイテムに対して、テストケースを作成する
    # test_cases = []
    # for golden in dataset.goldens:
    #     # print("golden:", golden)
    #     test_case = LLMTestCase(
    #         # LLM への入力文
    #         input=golden.input,
    #         # LLM からの出力文（回答）
    #         actual_output=golden.actual_output,
    #         # RAG用データセットなどの引用元のコンテキストで、HallucinationMetric等では必須パラメータになる
    #         # CoherenceMetric（文章の一貫性を評価）等では、不要パラメータになる
    #         context=golden.context,
    #     )
    #     print("test_case:", test_case)
    #     test_cases.append(test_case)
    # print("test_cases:", test_cases)

    # 品質評価指標の設定
    # AnswerRelevancyMetric: 回答の正確性を評価する指標
    # FaithfulnessMetric: 回答の忠実性を評価する指標
    # HallucinationMetric: 大規模言語モデル（LLM）の出力に含まれる「ハルシネーション」—つまり与えられたコンテキストや事実に基づかない情報の生成—を検出し評価するための指標
    # G-EvalMetric: 汎用的な言語モデル評価指標
    # ...
    # print("deepeval.metrics: ", dir(deepeval.metrics))

    answer_relevancy = AnswerRelevancyMetric(
        model=args.evaluation_model,
        threshold=args.threshold,
        # strict_mode=True,
        include_reason=True
    )
    summarization = SummarizationMetric(
        model=args.evaluation_model,
        threshold=args.threshold,
        # strict_mode=True,
        include_reason=True
    )

    # 品質評価の実行
    try:
        result = evaluate(
            test_cases=dataset.test_cases,
            metrics=[answer_relevancy, summarization],
            identifier="answer-relevancy and summarization"
        )
        print(result)
    except Exception as e:
        print(e)
