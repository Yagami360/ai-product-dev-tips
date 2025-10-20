# LangGraph を使用して簡単なマルチ AI Agent を作成する（プロンプト指定のみの AI Agent）

## 方法

1. LangChain をインストールする

    ```bash
    pip install -U langchain
    ```

1. LangGraph をインストールする

    ```bash
    pip install -U langgraph
    ```

1. その他 LangChain パッケージをインストールする

    ```bash
    pip install -U langchain-google-genai
    ```

1. LangGraph を使用したマルチ AI Agent のコードを実装する

    [agent.py](agent.py)

    ポイントは、以下の通り

    - LLM モデルを定義

        ```python
        # モデル定義
        model = init_chat_model(
            "google_genai:gemini-2.5-flash",
            temperature=0
        )
        ```

    - ２つの AI Agent を定義

        ```python
        def greeter_agent(state: dict):
            return {
                "messages": [
                    model.invoke(
                        [
                            SystemMessage(
                                content="You are a greeter in a friendly manner in Japanese."
                            )
                        ]
                        + state["messages"]
                    )
                ],
                "llm_calls": state.get('llm_calls', 0) + 1
            }

        def joke_agent(state: dict):
            return {
                "messages": [
                    model.invoke(
                        [
                            SystemMessage(
                                content="You are a joke generator in Japanese."
                            )
                        ]
                        + state["messages"]
                    )
                ],
                "llm_calls": state.get('llm_calls', 0) + 1
            }
        ```

        挨拶する AI Agent とジョークを言う AI Agent を `SystemMessage` のプロンプトので指定しただけの AI Agent にしている

    - `StateGraph` でグラフ（ワークフロー）を定義する

        ```python
        # Build workflow
        agent_builder = StateGraph(MessagesState)
        ```

        この際に、Graph 間に渡る情報を保持するクラスである State を渡す。
        今回の例では、ユーザーからの入力メッセージと LLM モデル呼び出し回数を保持する State になっている

        ```python
        class MessagesState(TypedDict):
            messages: Annotated[list[AnyMessage], operator.add]
            llm_calls: int
        ```

    - `StateGraph` オブジェクトの `add_node` メソッドで、グラフに上記 AI Agent のノードを追加する

        ```python
        # Add nodes
        agent_builder.add_node("greeter_agent", greeter_agent)
        agent_builder.add_node("joke_agent", joke_agent)
        ```

    - `StateGraph` オブジェクトの `add_edge` メソッドで、グラフ（ワークフロー）にエッジ（エージェント間の実行順を定義）を追加する

        ```python
        # Add edges to connect nodes
        agent_builder.add_edge(START, "greeter_agent")
        agent_builder.add_edge("joke_agent", "greeter_agent")
        agent_builder.add_edge("joke_agent", END)
        ```

        `START`（グラフの開始を表すエッジ） -> `greeter_agent` -> `joke_agent` -> `END`（グラフの終了を表すエッジ）の実行順になるようにする

    - `compile()` でグラフをコンパイルし、`invoke()` でグラフを実行する

        ```python
        # Compile the agent
        agent = agent_builder.compile()

        # Run Graph
        messages = [
            HumanMessage(content="何ができますか？"),
            HumanMessage(content="あいさつして"),
            HumanMessage(content="ジョークを言って")
        ]
        messages = agent.invoke({"messages": messages})
        ```

1. マルチ AI Agent のコードを実行する

    ```bash
    export GOOGLE_API_KEY="your-api-key-here"
    python agent.py
    ```

    ```bash
    ================================ Human Message =================================

    何ができますか？
    ================================ Human Message =================================

    あいさつして
    ================================ Human Message =================================

    ジョークを言って
    ================================== Ai Message ==================================

    私はあなたをお迎えし、楽しい時間を提供するためにここにいます！ジョークを言うこともできますよ！

    いらっしゃいませ！こんにちは！

    では、早速ですが、一つジョークをどうぞ！

    **パンはパンでも、食べられないパンはなーんだ？**
    ...
    ...
    ...
    **フライパン！**

    ふふ、どうでしたか？クスッと笑っていただけたら嬉しいです！他には何かお手伝いできることはありますか？
    ```

## 参考サイト

- https://docs.langchain.com/oss/python/langgraph/quickstart
- https://qiita.com/ksonoda/items/92a224e3f56255182140
