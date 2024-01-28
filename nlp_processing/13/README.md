# LangChain Agents の OpenAI Functions Agent を使用して Function calling を行う

LangChain でも OpenAI Functions Agent を使用すれば、OpenAI の Function calling 機能を簡単に使用することができる

> - OpenAI の Function calling 機能<br>
> 「[Function calling を使用して、入力文に応じて適切な外部関数の呼び出し、外部関数の戻り値に基づく出力文を生成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/12)」を使用することができる

## 使用方法

1. OpenAI SDK をインストールする
    ```sh
    pip3 install openai
    ```

1. LangChain をインストールする
    ```sh
    pip3 install langchain>=0.0.200
    ```

    > OpenAI Functions Agent は `0.0.200` 以降サポートされていることに注意

<!--
1. SerpAPI 用 Python ライブラリをインストールする
    今回の例では、Agent が実行する外部ツールとして SerpAPI（Google検索結果を取得してくれるAPIツール）を使用するのでインストールする
    ```sh
    pip3 install google-search-results
    ```
-->

1. OpenAPI キーを設定する
    ```sh
    export OPENAI_API_KEY=dummy
    ```

<!--
1. SerpAPI の API キーを発行する
    [SerpAPI のページ](https://serpapi.com/) から API キーを発行する
-->

1. OpenAI Functions Agent を使用した Python コードを作成する
    ```python
    import json
    import argparse

    from langchain.llms import OpenAI
    from langchain.agents import Tool
    from langchain.agents import initialize_agent
    from langchain.agents import AgentType
    # from langchain_community.utilities import SerpAPIWrapper


    def get_weather(location):
        if location in ["東京", "Tokyo"]:
            weather = "曇り"
        elif location in ["広島", "Hiroshima"]:
            weather = "晴れ"
        else:
            weather = "不明"

        resp = [
            {"天気": weather}
        ]

        # Function calling での外部関数は、json データで戻り値を返す必要あり
        return json.dumps(resp)


    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('--model_name', type=str, default="gpt-3.5-turbo-0613")     # OpenAI Functions Agent 対応のモデルを指定する必要あり
        parser.add_argument('--prompt', type=str, default="広島の天気を教えて")
        args = parser.parse_args()

        # ---------------------------------
        # モデル定義
        # ---------------------------------
        llm = OpenAI(
            model_name=args.model_name,
            temperature=0.0,
        )
        print("llm: ", llm)

        # ---------------------------------
        # LangChain Agents の Tools 定義
        # Tools : Agent が外部とやり取りをするために呼び出す外部関数や外部ツール
        # ---------------------------------
        tools = [
            Tool(
                name = "GetWeather",
                func=get_weather,
                description="天気を知りたい場所を入力。例: 東京"
            ),
            # Tool(
            #     name="GoogleSearch",
            #     func=SerpAPIWrapper().run,
            #     description="useful for when you need to answer questions about current events. You should ask targeted questions"
            # ),
        ]
        print("tools: ", tools)

        # ---------------------------------
        # Agent オブジェクト作成
        # ---------------------------------
        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.OPENAI_FUNCTIONS,    # AgentType.OPENAI_FUNCTIONS : OpenAI Functions Agent
            verbose=True,
        )

        # ---------------------------------
        # Agent 実行（LLM 推論で最適な外部ツール実行）
        # ---------------------------------
        try:
            resp = agent.run(input=args.prompt)
            print(f"resp: {resp}")
        except Exception as e:
            print(f"Excception was occurred | {e}")
            exit(1)

        exit(0)
    ```

    ポイントは、以下の通り

    - `initialize_agent()` メソッドの引数 `agent` に `AgentType.OPENAI_FUNCTIONS` を設定することで、OpenAI Functions Agent で FUnction calling を使用することができる

    - その他の部分は、通常の LangChain Agents と同じように使用できる
        > - 参考: [[In-progress]【Python】LangChain Agents を使用してプロンプトの内容に応じた外部ツールを実行する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/7)

1. Python コードを実行する

    - 外部関数を使用する場合
        ```sh
        python3 run_llm.py --prompt 広島の天気について教えて
        ```

        入力文「広島の天気について教えて」は、外部関数（今回の例では、都市の天気を返す関数）を使用する必要がある（使用しない場合は、「申し訳ありませんが、私の訓練データは2022年1月までのものであり、現在の天気情報を提供することはできません。広島の現在の天気予報を知りたい場合は、天気予報サイトや気象情報アプリを確認するか、地元の気象庁のウェブサイトを参照してください。」のような回答になる）ので、外部関数の呼び出しが行われる。この時の API からのレスポンスデータは、以下のようになる

        ```sh
        ```

    - 外部関数を使用せず通常の回答を行う場合
        ```sh
        python3 run_llm.py --prompt AIについて教えて
        ```

        入力文「AIについて教えて」は、外部関数（今回の例では、都市の天気を返す関数）を使用しなくてもいい一般的な質問文なので、外部関数の呼び出しは行われない。この時の API からのレスポンスデータは、以下のようになる。

        ```sh
        ```

## 参考サイト

- https://note.com/hamachi_jp/n/nbcaa7cff259d
- https://qiita.com/yu-Matsu/items/12b686fe4cab343f50b3#%E5%AE%9F%E3%81%AFagent%E3%81%A7%E3%82%82%E5%AF%BE%E5%BF%9C%E3%81%97%E3%81%A6%E3%81%84%E3%81%BE%E3%81%97%E3%81%9F
