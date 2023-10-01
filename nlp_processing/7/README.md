# 【Python】LangChain Agents を使用してプロンプトの内容に応じた外部ツールを実行する

LangChain Agents は、LLM を使って一連の外部ツール（例：Python スクリプトの実行、外部 API の実行など）を選択して実行できる機能になっている。<br>
Chains を使用すれば、同様の機能は実現可能であるが、Chain では Python スクリプトで一連の機能をハードコードする必要がある。一方エージェントでは、LLM を推論エンジンとして使用し、どの外部ツールをどの順番で実行するかを決定できる。

LangChain Agents には、以下の主要モジュールがある

- Agent
    プロンプトの内容に応じて適切な外部ツールを選択するための Agent

- Tools
    Agent が外部とやり取りをするために呼び出す関数

- Toolkits
    特定のユースケースに応じて、外部ツールを初期搭載した Agent 機能

- Agent Executor
    Agent の行動（最適な外部ツール選択）を実行するための機能（＝最適な外部ツール実行）

## 使用法

1. 各種 Python ライブラリをインストールする
    ```sh
    pip3 install openai
    pip3 install langchain
    ```

1. OpenAI の APIキーを発行する<br>
    [OpenAI Platform のページ](https://platform.openai.com/account/api-keys) から API キーを作成する<br>
    <img width="800" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/71ca027f-f4d2-4cde-9961-8a05da5ecf86">

1. SerpAPI 用 Python ライブラリをインストールする
    今回の例では、Agent が実行する外部ツールとして SerpAPI（Google検索結果を取得してくれるAPIツール）を使用するのでインストールする
    ```sh
    pip3 install google-search-results
    ```

1. SerpAPI の API キーを発行する
    [SerpAPI のページ](https://serpapi.com/) から API キーを発行する

1. LangChain Agents を使用した Python コードを作成する<br>

    - Tools で既存の外部ツールを使用する場合のコード例 : `run_langchain_1.py`
        ```python
        import os
        import argparse

        from langchain.llms import OpenAI

        from langchain.agents import Tool
        from langchain.agents import load_tools
        from langchain.agents import initialize_agent
        from langchain.agents import AgentType

        if __name__ == '__main__':
            parser = argparse.ArgumentParser()
            parser.add_argument('--openai_api_key', type=str, default="dummuy")
            parser.add_argument('--model_name', type=str, default="text-davinci-003")
            parser.add_argument('--serp_api_key', type=str, default="dummuy")
            args = parser.parse_args()

            os.environ["SERPAPI_API_KEY"] = args.serp_api_key

            # ---------------------------------
            # モデル定義
            # ---------------------------------
            llm = OpenAI(
                openai_api_key=args.openai_api_key,
                model_name=args.model_name,
                temperature=0.9,    # 大きい値では出現確率が均一化され、より多様な文章が生成される傾向がある。低い値では出現確率の高い単語が優先され、より一定の傾向を持った文章が生成される傾向がある。
            )
            print("llm: ", llm)

            # ---------------------------------
            # LangChain Agents の Tools 定義
            # Tools : Agent が外部とやり取りをするために呼び出す外部関数や外部ツール
            # ---------------------------------
            tools = load_tools(
                [
                    "serpapi",      # serpapi : Google 検索結果を取得する外部 API ツール
                    "llm-math",     # llm-math : 算術計算をする LangChain ツール
                ],
                llm=llm
            )

            # Tool(name='Search', description='A search engine. Useful for when you need to answer questions about current events. Input should be a search query.' ... )
            # Tool(name='Calculator', description='Useful for when you need to answer questions about math.' ... )
            print("tools: ", tools)

            # ---------------------------------
            # Agent オブジェクト作成
            # ---------------------------------
            agent = initialize_agent(
                tools,
                llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,    # AgentType.ZERO_SHOT_REACT_DESCRIPTION : Tools オブジェクトの `description` フィールドなどから、どのツールを用いるかを決める Agent
                verbose=True
            )

            # ---------------------------------
            # Agent 実行（LLM 推論で最適な外部ツール実行）
            # ---------------------------------
            try:
                response = agent.run("""
                今日の広島市の最高気温を教えて。
                そして、最高気温を2乗した結果を教えて。
                """)
                print(f"response: {response}")
            except Exception as e:
                print(f"Excception was occurred | {e}")
                exit(1)

            exit(0)
        ```

        ポイントは、以下の通り

        - `load_tools()` で外部ツールを定義する。今回の例では既存の定義済み外部ツールの `"serpapi"`, `"llm-math"` を使用する

            - その他既存ツールに関しては、以下を参照
                - https://book.st-hakky.com/docs/agents-of-langchain/#%E4%BB%A3%E8%A1%A8%E7%9A%84%E3%81%AA%E3%83%84%E3%83%BC%E3%83%AB%E3%81%AE%E4%B8%80%E8%A6%A7

            - 独自の外部ツールを定義する場合は、自身で Tool オブジェクトを定義し、ツールのリストに追加する
                ```python
                tools.append(
                    Tool(
                        name="duckduckgo-search",
                        func=search.run,
                        description="useful for when you need to search for latest information in web"
                    ),
                    ...
                )
                ```

        - `initialize_agent()` メソッドで Agent オブジェクトを作成する。この際に Agent の種類（Agent Types）を指定する
            - 今回の例では、zero-shot-react-description（`AgentType.ZERO_SHOT_REACT_DESCRIPTION`）の Agent 作成
                - 他にも以下のような Agent が作成する
                    - react-docstore : 文書を扱うことに特化したAgent
                    - self-ask-with-search : 質問に対する答えを事実に基づいて調べてくれるAgent
                    - conversational-react-description : 
                    - その他の Agent Types に関しては、以下を参照
                        - https://python.langchain.com/docs/modules/agents/agent_types/

            - `AgentType.ZERO_SHOT_REACT_DESCRIPTION` では、Tool オブジェクトのツール説明文章フィールド `description` などから、どのツールを用いるかを決めている
                ```sh
                Tool(
                    name='Search',
                    description='A search engine. Useful for when you need to answer questions about current events. Input should be a search query.',
                    ...
                ),
                Tool(
                    name='Calculator',
                    description='Useful for when you need to answer questions about math.',
                    ...
                )
                ```
        
        - `agent.run("質問文")` で Agent を実行する。この部分が AgentExecutor の機能になる
 
    - Tools で独自の外部ツールの使用する場合のコード例 : `run_langchain_2.py`
        ```python
        ```

    - Toolkits を使用したコード例 : `run_langchain_3.py`
        ```python
        ```

1. Python コードを実行する<br>
    - `run_langchain_1.py`
        ```sh
        python3 run_langchain_1.py
        ```

        出力結果は、以下の通り

        ```sh
        > Entering new AgentExecutor chain...
        Searching for the current high temperature in Hiroshima City 
        Action: Search
        Action Input: 高温 広島市
        Observation: 今日4日(月)、中国地方は北風によるフェーン現象により瀬戸内側で猛暑となり、広島市では14時12分に最高気温が37.4℃となり、過去9月の最高記録を ...
        Thought: Using a Calculator to calculate the result of squaring the high temperature 
        Action: Calculator
        Action Input: 37.4 * 37.4
        Observation: Answer: 1398.76
        Thought: I now have the answer
        Final Answer: 最高気温は37.4℃、最高気温を2乗した結果は1398.76です。

        > Finished chain.
        response: 最高気温は37.4℃、最高気温を2乗した結果は1398.76です。
        ```

        - 質問文「今日の広島市の最高気温を教えて。そして、最高気温を2乗した結果を教えて。」に対して、まず外部ツールの SerpAPI を用いて、今日の広島市の最高気温を Google 検索し、その後外部ツールの LLM Math を用いて最高気温を計算しており、質問文に対して最適な外部ツールを呼び出している

        - `Action: Search` の部分が、`"serpapi"` の Tool オブジェクトの name `Search` に対応
            ```sh
            Tool(
                name='Search',
                description='A search engine. Useful for when you need to answer questions about current events. Input should be a search query.',
                ...
            ),
            ```

        - `Action: Calculator` の部分が、`"llm-math"` の Tool オブジェクトの name `Calculator` に対応
            ```sh
            Tool(
                name='Search',
                description='A search engine. Useful for when you need to answer questions about current events. Input should be a search query.',
                ...
            ),
            ```

## 参考サイト

- https://python.langchain.com/docs/modules/agents/
- https://zenn.dev/umi_mori/books/prompt-engineer/viewer/langchain_agents