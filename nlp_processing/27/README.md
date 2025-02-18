# DeepEval を使用して LLM からの回答の品質評価を行う

## 使用方法

1. DeepEval のインストール<br>
    ```bash
    pip3 install deepeval
    ```

1. DeepEval を使用した LLM からの回答の品質評価のスクリプトを作成する<br>
    - コード例: `run.py`
        ```python
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
    ```
