# LangGraph Server を使用して AI Agent 作成＆管理用 API サーバーを起動する

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

1. LangGraph Server のプロンプトのテンプレートを作成する

    ```bash
    langgraph new server-agent --template new-langgraph-project-python
    ```

    ```bash
    /server-agent
    + /src/agent
    + --- grapy.py     # LangGraph でのグラフ（ワークフロー）定義のコード。テンプレート時点では、START -> END 空のグラフが定義されているのみ
    ```

1. 環境変数を設定する

    ```bash
    cp .env.example .env
    ```

    上記コマンドで作成された環境変数のファイル例 `.env.example` から `.env` を作成し、必要な環境変数を設定する

    - `LANGSMITH_PROJECT`: LangSmith のプロジェクト
    - `LANGSMITH_API_KEY`: LangSmith の API キー（LangSmith コンソール UI の[設定]から作成可能）

1. LangGraph Server を起動する

    LangGraph CLI コマンド `langgraph` で起動する

    ```bash
    cd server-agent
    langgraph dev
    ```

    ```bash
    INFO:langgraph_api.cli:

            Welcome to

    ╦  ┌─┐┌┐┌┌─┐╔═╗┬─┐┌─┐┌─┐┬ ┬
    ║  ├─┤││││ ┬║ ╦├┬┘├─┤├─┘├─┤
    ╩═╝┴ ┴┘└┘└─┘╚═╝┴└─┴ ┴┴  ┴ ┴

    - 🚀 API: http://127.0.0.1:2024
    - 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
    - 📚 API Docs: http://127.0.0.1:2024/docs

    This in-memory server is designed for development and testing.
    For production use, please use LangSmith Deployment.
    ```

1. LangSmith のコンソール UI から確認する

    ```bash
    open https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
    ```

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/b1641426-5ca7-4814-8a8e-381a4d9805d8" />

    LangGraph Server によって、AI Agent 作成＆管理用 API サーバーとしてデプロイされているので、LangSmith のコンソール UI 経由で実行できる

    > A2A もデフォルトでサポートされており、A2A プロンプトでの API 通信もサポートしている

1. [Option] API ドキュメントのコンソール UI を確認する

    ```open
    open http://127.0.0.1:2024/docs
    ```

    LangGraph Server によってデプロイされる API は、AI Agent 作成＆管理するために必要な各種 API が存在する API になっている

    > 個々の AI Agent 自体の API サーバーではなく、AI Agent 作成＆管理用の API サーバーであることに注意

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/9f257bb6-5538-48d6-bfc4-0d78b48a74e7" />

    また、各 API エンドポイントをコンソール UI から直接テストすることもできる

    <img width="721" height="370" alt="Image" src="https://github.com/user-attachments/assets/2c2098e7-8655-4a3c-b680-1f2ff665dfe0" />

## 参考サイト

- https://docs.langchain.com/oss/python/langgraph/local-server
