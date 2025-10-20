# Google ADK を使用して簡単なマルチ AI Agent を作成する（プロンプト指定のみの AI Agent）

## 方法

1. Google ADK の Python パッケージをインストールする

    ```bash
    pip install google-adk
    ```

1. Google ADK コマンドでプロジェクトのテンプレートを作成する

    ```bash
    adk create multi_agent
    ```

    ```bash
    Choose a model for the root agent:
    1. gemini-2.5-flash
    2. Other models (fill later)

    Choose model (1, 2): 1
    1. Google AI
    2. Vertex AI
    Choose a backend (1, 2): 1

    Don't have API Key? Create one in AI Studio: https://aistudio.google.com/apikey
    Enter Google API key: xxx
    ```

    今回は、Google AI Studio で作成する

    コマンド完了後、以下のディレクトリ構成でテンプレートが作成される

    ```sh
    multi_agent/
        agent.py      # main agent code
        .env          # API keys or project IDs
        __init__.py
    ```

    > .env に API キーが保存されるので、GitHub に公開しないこと

1. Google ADK を使用した マルチ AI Agent のコードを実装する

    今回のケースでは、簡単のためプロンプトで指示した複数 AI Agent のコードを実装する

    - ワークフローを使用せず、Agent 階層構造のみ使用した マルチ AI Agent を構築する場合：`Parent agent`, `Sub Agents`

        [agent.py](multi_agent/agent.py)

    - 直列処理でのマルチ AI Agent を構築する場合：`SequentialAgent`

        [agent.py](multi_agent_sequential/agent.py)

    - 並列処理をでのマルチ AI Agent を構築する場合：`ParallelAgent`


1. Google ADK を使用した マルチ AI Agent のコードを実行する

    - ワークフローを使用せず、Agent 階層構造のみ使用した マルチ AI Agent を構築する場合：`Parent agent`, `Sub Agents`

        ```bash
        adk run multi_agent
        ```
        ```bash
        [user]: 何ができますか？
        [MultiAgentWithHierarchy]: ご挨拶とジョークを担当しています。どちらにご興味がありますか？
        [user]: あいさつして
        [Greeter]: こんにちは！

        [user]: ジョークを言って
        [JokeGenerator]: パンはパンでも、食べられないパンはなーんだ？

        …フライパン！
        ```

        挨拶する AI Agent とジョークを言う AI Agent のみの簡単なマルチ AI Agent になっている。また、この２つの AI Agent をサブエピソードが、適切な AI Agent に割り振る構造になっている

    - 直列処理でのマルチ AI Agent の場合

        ```bash
        adk run multi_agent_sequential
        ```
        ```bash
        [user]: 何ができますか？
        [Greeter]: こんにちは！何かお手伝いできることはありますか？

        [JokeGenerator]: パンはパンでも、食べられないパンはなーんだ？

        ...フライパン！
        ```

        `SequentialAgent` での直列処理により、１回のユーザー質問で、挨拶する AI Agent とジョークを言う AI Agent それぞれが直列処理で回答を行うマルチ AI Agent になっている

    - 並列処理でのマルチ AI Agent の場合

        ```bash
        adk run multi_agent_parallel
        ```
        ```bash
        [user]: 何ができますか？
        [Greeter]: こんにちは！何かお手伝いできることはありますか？ 😊

        [JokeGenerator]: ジョークを作れます！何か面白い話を聞きたいですか？
        ```

        `ParallelAgent` での並列処理により、１回のユーザー質問で、挨拶する AI Agent とジョークを言う AI Agent それぞれが並列処理で回答を行うマルチ AI Agent になっている

1. [Option] Google ADK を使用した AI Agent のサンプルコードをコンソール UI で動かす

    ```bash
    adk web --port 8000
    ```

    - ワークフローを使用せず、Agent 階層構造のみ使用した マルチ AI Agent を構築する場合：`Parent agent`, `Sub Agents`

        xxx

    - 直列処理でのマルチ AI Agent の場合

        xxx

    - 並列処理でのマルチ AI Agent の場合

        xxx

## 参考サイト

- https://google.github.io/adk-docs/agents/multi-agents/
- https://zenn.dev/google_cloud_jp/articles/c5fa102f468cdf#%E3%82%A8%E3%83%BC%E3%82%B8%E3%82%A7%E3%83%B3%E3%83%88%E3%81%AE%E4%BD%9C%E6%88%90
