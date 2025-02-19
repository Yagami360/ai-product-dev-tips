# DeepEval を使用して LLM からの回答の品質評価を行う

## 使用方法

1. DeepEval のインストール<br>
    ```bash
    pip3 install deepeval
    ```

    > 2025-02-17 時点で、Python 3.10 で動作確認済み

1. DeepEval を使用した LLM からの回答の品質評価のスクリプトを作成する<br>
    - コード例: `run.py`
        ```python
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
                input="アインシュタインの相対性理論について説明してください",
                actual_output="アインシュタインは特殊相対性理論と一般相対性理論を発表しました...",
                context=["アルベルト・アインシュタインは1905年に特殊相対性理論を、1915年に一般相対性理論を発表した..."]
            )

            # 評価指標の設定
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

            # 評価の実行
            try:
                result = evaluate([test_case], [metric])
                print(result)
            except Exception as e:
                print(e)
        ```

1. 各種 API キーを設定する<br>
    DeepEval では、内部で OpenAI の API を使用しているため、OpenAI の API キーを設定する必要がある。
    ```bash
    export OPENAI_API_KEY=${OPENAI_API_KEY:-"dummy"}
    ```

1. 評価スクリプトを実行する<br>
    ```bash
    python3 run.py
    ```

1. 評価結果を確認する<br>
    ```bash
    ======================================================================

    Metrics Summary

    - ✅ Hallucination (score: 0.0, threshold: 0.3, strict: False, evaluation model: gpt-4o, reason: The score is 0.00 because the actual output fully aligns with the given contexts without any contradictions, despite a slight lack of specificity., error: None)

    For test case:

    - input: アインシュタインの相対性理論について説明してください
    - actual output: アインシュタインは特殊相対性理論と一般相対性理論を発表しました...
    - expected output: None
    - context: ['アルベルト・アインシュタインは1905年に特殊相対性理論を、1915年に一般相対性理論を発表した...']
    - retrieval context: None

    ======================================================================

    Overall Metric Pass Rates

    Hallucination: 100.00% pass rate

    ======================================================================
    ```

