# 【Python】LangSmith を使用して UI コンソール上から LLM アプリケーションの実行トレースと実行ログを確認する

LangSmith は、2023/7/21 月頃に新規追加された LangChain の機能（2023/08/26 時点では、クローズドベータ版機能）の１つで、LLM アプリケーションの本番運用であると便利な以下の機能郡を織り込んだ UI コンソール付きのモジュールになっている。

- LLM アプリケーションの実行トレースや実行ログのモニタリング機能<br>
    LLM アプリケーションの実行トレースや実行ログを LangSmith UI コンソール上で容易に確認できる。<br>
    具体的には、LangChain で実装した LLM アプリケーションの各コンポーネントの入力と出力の実行トレースや実行ログを UI コンソール上で確認することができる<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/5f8dd200-05e4-44a1-8863-7b553389b79b"><br>

    また、LLM アプリケーションを一度実行し実行トレースを取得できれば、LLM アプリケーション内部で使用している LLM モデルのパラメーター（temperature など）を LangSmith コンソール UI 上から直接変更して、LLM アプリケーションの出力がどうなるかを確認できる。<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/8b3fa58f-f025-4d30-966a-e3f05b3253e7"><br>
    
- LLM アプリケーションの出力をデータセットとして保存＆収集する機能<br>
    LLM アプリケーションの実行ログの出力結果をデータセットとして保存することができる。<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/d493b1e7-41d5-463f-8c40-6dbf8188ae51"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/f24a0ee9-20ff-4ef3-8d35-26ea600ecd97"><br>

- LLM アプリケーションのテストと評価機能<br>
    LangSmith コンソール UI 上に登録したデータセットを用いて、LLM アプリケーションの品質評価（LLM モデルの品質評価など）を行うとこができる<br>
    具体的には、ユーザーの質問文に対しての LLM アプリケーションの回答出力に対して、登録したデータセットの正解データとを比較して、正しい回答であるかのスコアをコンソール UI 上から簡単に確認することができる

> LangChain 自体も、LLM アプリケーションを構築する上で必要となる各種機能郡を組み込んだライブラリであったが、LangSmith では更に本番運用であると便利な上記機能郡が追加されている

## 使用方法

1. LangSmith のアカウントを作成する
    [こちらのページ](https://smith.langchain.com/)から LangSmith のアカウントを作成する

1. waitlist に登録する<br>
    LangSmith は、現時点（2023/08/26）でクローズドベータ版機能であり、一部ユーザーにしか開放されていないので、[こちらのページ](https://6w1pwbss0py.typeform.com/to/RS6P2o8s?typeform-source=www.langchain.com)から waitlist に登録する

1. 利用許可で出るまで待つ<br>

1. LangChain の API キーを作成する<br>
    [LangSmith コンソール UI](https://smith.langchain.com/) の「API Keys」ボタンをクリックし、LangChain の API キーを作成する

1. LangChain の Python SDK をインストールする
    ```sh
    pip3 install langchain
    ```

    > LangSmith は LangChain の１機能であり、LangChain の Python SDK から利用できる

1. 実行ログを取得するための各種 LangChain 用環境変数を設定する
    ```sh
    export LANGCHAIN_TRACING_V2=true
    export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
    export LANGCHAIN_API_KEY=<your-api-key>
    export LANGCHAIN_PROJECT=<your-project>  # if not specified, defaults to "default"
    ```
    - `LANGCHAIN_API_KEY` : 上記作成した LangChain の API キー

1. OpenAI の API 用キーを設定する
    ```sh
    export OPENAI_API_KEY='dummy'
    ```

1. LangChain を使用した LLM アプリケーションのコードを実装する<br>
    ここでは、最も簡単な例として、以下のようなコードを作成する

    - `run_llm_call.py`
        ```python
        from langchain.chat_models import ChatOpenAI

        llm = ChatOpenAI()
        llm.predict("Hello, world!")
        ```

1. 上記実装した LLM アプリケーションを実行する<br>
    ```sh
    python3 run_llm_call.py
    ```

    > LangChain を使用した LLM アプリケーションのコードを実行すると、その実行トレースが LangSmith コンソール UI から確認できるようになる

1. LangSmith のコンソール UI から実行ログを確認する<br>
    [LangSmith コンソール UI](https://smith.langchain.com/) の「Projects」ページの対象プロジェクト（`LANGCHAIN_PROJECT`）から、上記実装した LLM アプリケーションの実行ログを確認する

    - 全体画面<br>
       <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/4bbdff2a-4043-4e17-b676-2b1805025c5c">
    
    - トレース画面<br>
        <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/b180d40e-660e-461a-8cc5-e4ec93d26f1b">
        - 入力プロンプトと応答文のペアが確認できる

    - モニター画面
        <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/d60ab701-1565-4af7-b394-ff367c7f9902">

1. 【オプション】実行トレースの LLM モデルのパラメーターなどをLangSmith コンソール UI 上から直接修正し、出力を再確認する<br>
    LLM アプリケーションを一度実行し、実行トレースを取得できれば、LLM アプリケーション内部で使用している LLM モデルのパラメーター（temperature など）を LangSmith コンソール UI 上から直接変更して、LLM アプリケーションの出力がどうなるかを確認できる。
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/8b3fa58f-f025-4d30-966a-e3f05b3253e7">


## 参考サイト

- https://docs.smith.langchain.com/
- https://zenn.dev/umi_mori/articles/langchain-langsmith
