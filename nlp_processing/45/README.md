# Google ADK を使用して簡単な AI Agent を作成する（プロンプト指定のみの AI Agent）

## 方法

1. Google ADK の Python パッケージをインストールする

    ```bash
    pip install google-adk
    ```

1. Google ADK コマンドでプロジェクトのテンプレートを作成する

    ```bash
    adk create my_agent
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
    my_agent/
        agent.py      # main agent code
        .env          # API keys or project IDs
        __init__.py
    ```

    > .env に API キーが保存されるので、GitHub に公開しないこと

1. Google ADK を使用した AI Agent のサンプルコードを実行する

    ```bash
    adk run my_agent
    ```

    ```bash
    (base) yusukesakai@YusukenoMacBook-Pro 45 % adk run my_agent
    Log setup complete: /var/folders/p3/mll4bqln1mz3wt4y6w_wqnmc0000gq/T/agents_log/agent.20251017_142433.log
    To access latest log: tail -F /var/folders/p3/mll4bqln1mz3wt4y6w_wqnmc0000gq/T/agents_log/agent.latest.log
    /opt/anaconda3/lib/python3.12/site-packages/google/adk/cli/cli.py:154: UserWarning: [EXPERIMENTAL] InMemoryCredentialService: This feature is experimental and may change or be removed in future versions without notice. It may introduce breaking changes at any time.
    credential_service = InMemoryCredentialService()
    /opt/anaconda3/lib/python3.12/site-packages/google/adk/auth/credential_service/in_memory_credential_service.py:33: UserWarning: [EXPERIMENTAL] BaseCredentialService: This feature is experimental and may change or be removed in future versions without notice. It may introduce breaking changes at any time.
    super().__init__()
    Running agent root_agent, type exit to exit.
    /opt/anaconda3/lib/python3.12/site-packages/google/adk/cli/cli.py:98: UserWarning: [EXPERIMENTAL] App: This feature is experimental and may change or be removed in future versions without notice. It may introduce breaking changes at any time.
    else App(name=session.app_name, root_agent=root_agent_or_app)
    [user]: 何ができますか？        
    [root_agent]: 私は、質問に答えたり、情報を探したり、クリエイティブなコンテンツを生成したり、さまざまなタスクであなたを助けることができます。具体的には、以下のようなことができます。

    *   **質問に答える:** 事実に基づいた情報を提供したり、一般的な知識について説明したりします。
    *   **テキストの生成:** 物語、詩、コード、スクリプト、音楽作品、メール、手紙など、さまざまな種類のクリエイティブなテキスト形式を生成できます。
    *   **要約:** 長い文章や記事を短くまとめて、主要なポイントを把握しやすくします。
    *   **翻訳:** 多くの言語間でテキストを翻訳できます。
    *   **アイデア出し:** 特定のテーマやプロジェクトについて、新しいアイデアを提案できます。
    *   **複雑なトピックの解説:** 難しい概念やトピックを、分かりやすい言葉で説明します。
    *   **情報検索:** 特定のテーマに関する情報を探し出し、提供します。

    何かお手伝いできることがあれば、お気軽にお申し付けください！
    ```

1. Google ADK を使用した AI Agent のサンプルコードをコンソール UI で動かす

    ```bash
    adk web --port 8000
    ```

    上記コマンド実行後、ブラウザで `http://127.0.0.1:8000` を開く
    ```bash
    open http://127.0.0.1:8000
    ```

    以下のようなチャット形式でのコンソール UI で AI Agent を動かすことができる

    <img width="899" alt="Image" src="https://github.com/user-attachments/assets/c99fa3d5-b20e-4cb9-8982-5c86f44780a3" />

## 参考サイト

- https://google.github.io/adk-docs/get-started/python/#installation
