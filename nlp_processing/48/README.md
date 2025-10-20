# Google ADK を使用してA2A 対応 AI Agent を作成する

```bash
+-------------------------+         +-----------------------------------+
| Customer Service Agent  |         |         RemoteA2aAgent            |
| (Your Root Agent)       |<------->|         (ADK Client Proxy)        |
+-------------------------+         |                                   |
                                    |  +-----------------------------+  |
                                    |  |     Product Catalog Agent   |  |
                                    |  |      (External Service)     |  |
                                    |  +-----------------------------+  |
                                    +-----------------------------------+
                                                 |
                                                 | (Network Communication)
                                                 v
                                               +-----------------+
                                               |   A2A Server    |
                                               | (ADK Component) |
                                               +-----------------+
                                                       |
                                                       v
                                               +------------------------+
                                               | Product Catalog Agent  |
                                               | (Exposed Service)      |
                                               +------------------------+
```

## 方法

1. Google ADK の Python パッケージをインストールする

    ```bash
    pip install google-adk
    ```

1. Google ADK コマンドでプロジェクトのテンプレートを作成する

    ```bash
    adk create a2a_agent
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
    a2a_agent/
        agent.py      # main agent code
        .env          # API keys or project IDs
        __init__.py
    ```

    > .env に API キーが保存されるので、GitHub に公開しないこと

1. Google ADK を使用した A2A 対応 AI Agent のコードを実装する

    - [agent.py](a2a_agent/agent.py)

        A2A Agent を呼び出す AI Agent

    - [a2a_agent/agent.py](a2a_agent/agent.py)

        A2A 対応 AI Agent

        ポイントは、以下の通り

        - 通常の AI Agent 定義（`LlmAgent` など使用）を行い、`to_a2a()` メソッドを呼び出すだけで A2A 対応 AI Agent が作成できる

        - A2A 対応 AI Agent は、uvicorn を使用した API サーバーとして動作する（次のステップで、`uvicorn` コマンドで API サーバー起動）

            - `to_a2a()` メソッドは、`LlmAgent` 等で定義した AI エージェントからスキル、機能（tools）、メタデータを抽出することで、裏でメモリ内に `AgentCard` オブジェクトを自動生成します。これにより、uvicorn を使用してエージェントエンドポイントが API デプロイされる際に、デフォルトの `AgentCard` が利用可能になる。

            - `AgentCard` は自身で定義することも可能

1. A2A Agent の API サーバーを起動する

    ```bash
    python -m uvicorn a2a_agent.agent:a2a_app --host localhost --port 8001
    ```

1. [Optional] Agent Card を確認する

    ```bash
    curl http://localhost:8001/.well-known/agent-card.json
    ```

    ```json
    {
        "capabilities": {},
        "defaultInputModes": [
            "text/plain"
        ],
        "defaultOutputModes": [
            "text/plain"
        ],
        "description": "I greet the user.",
        "name": "Greeter",
        "preferredTransport": "JSONRPC",
        "protocolVersion": "0.3.0",
        "skills": [
            {
                "description": "I greet the user. Greet the user in a friendly manner in Japanese.",
                "id": "Greeter",
                "name": "model",
                "tags": [
                    "llm"
                ]
            }
        ],
        "supportsAuthenticatedExtendedCard": false,
        "url": "http://localhost:8001",
        "version": "0.0.1"
    }
    ```

1. A2A 対応 AI Agent を実行する

<!--
    - Python コードから実行する場合

        ```bash
        python agent.py
        ```
-->

    - コンソール UI で実行する場合

        ```bash
        adk web --port 8000
        ```

## 参考サイト

- https://google.github.io/adk-docs/a2a/
- https://google.github.io/adk-docs/a2a/quickstart-exposing/#exposing-the-remote-agent-with-the-to_a2aroot_agent-function
- https://github.com/google/adk-python/tree/main/contributing/samples/a2a_root