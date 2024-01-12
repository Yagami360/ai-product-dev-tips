# 【Python】 LangSmith の Evaluation 機能を使用して、データセット化した入出力履歴の評価スコアを表示する

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

1. LangSmith のデータセットを作成する<br>

    - コンソール UI から行う場合<br>

    - SDK で行う場合<br>
        ```python
        ```

1. LangSmith の Evaluation を実行する<br>
    ```python
    ```

    evalutors の種類には、以下のようなものが存在する

    - QA 用の evalutors で、ユーザの入出力に対する応答の "Correctness"（正しさ）を計測できる
        - `"context_qa"` : LLM Chain が "Correctness"（正しさ）を判断する際に、(出力例を通して提供される) "context"（参照）情報を使用するように指示する。大規模なコーパスを持っているが、入力文に対する教師データ（正解データ）を持っていない場合に便利。
        - `"qa"` : LLM Chain に、教師データ（正解データ）に基づいて「"correct"（正解）」または「"incorrect"（不正解）」として入出力文をスコア化。
        - `"cot_qa"` : `"context_qa"` と似ているが、最終的な評価スコアを決定する前に、"chain of thought"（思考の連鎖）での「推論」を使用するように LLMChain に指示する。これは、トークンとランタイムコストが若干高くなる代わりに、人間のラベルとより良い相関を持つ応答を導く傾向がある。

    - `"criteria"`: 教師データなしでの評価

    - `"labeled_criteria"` : 

    - `"embedding_distance"` : 

    - `"string_distance"` : 

1. LangSmith のコンソール UI から評価スコアの結果を確認する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/482ad737-8d18-46fa-8b5a-8eeb45328f91"><br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/c5ea0420-ab75-4e09-aed2-07d7fc06ffdb"><br>
