# DeepEval を使用してデータセットの品質評価を行う

## 使用方法

1. DeepEval のインストール<br>
    ```bash
    pip3 install deepeval
    ```
    > 2025-02-17 時点で、Python 3.10 で動作確認済み

1. DeepEval のコンソール UIである [Confident-AI](https://app.confident-ai.com/) からデータセットを作成する<br>
    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/bad4a9c0-f4f1-4318-ad85-54c5b985e015" />

1. DeepEval を使用したデータセットの品質評価のスクリプトを作成する<br>
    - コード例: `[run.py](./run.py)`

1. DeepEval のコンソール UIである [Confident-AI](https://app.confident-ai.com/) にログインする
    ```sh
    deepeval login
    ```

    ```sh
    Welcome to ✨DeepEval✨!
    Login and grab your API key here: https://app.confident-ai.com/pair?code=DVU8BK&port=57457
    Paste your API Key:
    ```
    DeepEval の API キーの入力が求められるので、入力する（APIキーは、Confident-AI 初回セットアップ時に作成可能）

1. 各種 API キーを設定する<br>
    DeepEval では、内部で OpenAI の API を使用しているため、OpenAI の API キーを設定する必要がある。
    ```bash
    export OPENAI_API_KEY=${OPENAI_API_KEY:-"dummy"}
    ```

1. 評価スクリプトを実行する<br>
    ```bash
    python3 run.py
    ```

1. DeepEval のコンソール UIである [Confident-AI](https://app.confident-ai.com/) から評価結果を確認する<br>

    - 各テストケースの概要<br>
        <img width="1200" alt="Image" src="https://github.com/user-attachments/assets/baff5935-6a09-4874-a40b-9cabc17fcc0e" />

    - 各テストケースの詳細<br>
        <img width="1200" alt="Image" src="https://github.com/user-attachments/assets/a516791e-649b-4749-bf64-74b5272d8433" />