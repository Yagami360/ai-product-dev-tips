# LangGraph Server を使用して簡単な A2A 対応 AI Agent を作成する

## 方法

1. LangChain をインストールする

    ```bash
    pip install -U langchain
    ```

1. LangGraph をインストールする

    ```bash
    pip install -U langgraph
    ```

1. LangGraph CLI をインストールする

    ```bash
    pip install -U "langgraph-cli[inmem]"
    ```

1. LangGraph API をインストールする

    ```bash
    pip install "langgraph-api>=0.4.9"
    ```

1. LangGraph Server のプロンプトのテンプレートを作成する

    ```bash
    langgraph new a2a-agent --template new-langgraph-project-python
    ```

    ```bash
    /server-agent
    + /src/agent
    + --- grapy.py      # LangGraph でのグラフ（ワークフロー）定義のコード。テンプレート時点では、START -> END 空のグラフが定義されているのみ
    + pyproject.toml    # 依存パッケージ等の定義
    ```

1. `pyproject.toml` に必要なパッケージを追加する

    今回の例では、Gemini モデルを使用するので、`langchain-google-genai` を追加する

1. 環境変数を設定する

    ```bash
    cp .env.example .env
    ```

    上記コマンドで作成された環境変数のファイル例 `.env.example` から `.env` を作成し、必要な環境変数を設定する

    - `LANGSMITH_PROJECT`: LangSmith のプロジェクト
    - `LANGSMITH_API_KEY`: LangSmith の API キー（LangSmith コンソール UI の[設定]から作成可能）
    - ``

1. LangGraph API を使用した AI Agent（Graph）のコードを実装する

    テンプレートで作成された [a2a-agent/src/agent/graph.py](a2a-agent/src/agent/graph.py) のコードを書き換えて実装する

    ポイントは、以下の通り

    - **A2A 対応のために特別なメソッド等を呼び出す必要はなく、LangGraph の標準機能としてサポートされている**

    - 今回の例では、Genimi モデルを使用した AI Agent の Graph にしている

1.  LangGraph Server を起動する

    LangGraph CLI コマンド `langgraph` で起動する

    ```bash
    langgraph dev
    ```

1. デプロイした API の AgentCard を確認する

    assistant_id を取得

    ```bash
    curl GET http://127.0.0.1:2024/assistants/search
    ```

    A2A Agent の AgentCard を確認する
    ```
    curl -X GET "http://127.0.0.1:2024/.well-known/agent-card.json?assistant_id=fe096781-5601-53d2-b2f6-0d3403f7e9ca" | jq .
    ```

    ```json
    {
        "protocolVersion": "0.3.0",
        "name": "agent",
        "description": "agent assistant",
        "url": "http://127.0.0.1:2024/a2a/fe096781-5601-53d2-b2f6-0d3403f7e9ca",
        "preferredTransport": "JSONRPC",
        "capabilities": {
            "streaming": true,
            "pushNotifications": false,
            "stateTransitionHistory": false
        },
        "defaultInputModes": [
            "application/json",
            "text/plain"
        ],
        "defaultOutputModes": [
            "application/json",
            "text/plain"
        ],
        "skills": [
            {
                "id": "fe096781-5601-53d2-b2f6-0d3403f7e9ca-main",
                "name": "agent Capabilities",
                "description": "agent assistant",
                "tags": [
                    "assistant",
                    "langgraph"
                ],
                "examples": [],
                "inputModes": [
                    "application/json",
                    "text/plain"
                ],
                "outputModes": [
                    "application/json",
                    "text/plain"
                ],
                "metadata": {
                    "inputSchema": {
                    "required": [
                        "messages"
                    ],
                    "properties": [
                        "messages"
                    ],
                    "supportsA2A": true
                    }
                }
            }
        ],
        "version": "0.4.44"
    }
    ```

    A2A 通信に必要な Agent Card が自動的に設定されている

    また、A2A のための API もデフォルトで提供されており、上記自動的に設定される Agent Card と API により、デフォルトで A2A での API 通信もサポートされている。

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/e688b07e-66d7-4b40-a647-05c8e62a8fe7" />

1. LangSmith のコンソール UI から A2A 経由で AI Agent を動かす

    ```bash
    open https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
    ```

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/d1e91156-4d36-4138-84cd-d3746e476405" />

    A2A 経由で、ユーザーからの質問に対し、Genimi モデルで回答できている


## 参考サイト

- https://docs.langchain.com/langsmith/server-a2a
