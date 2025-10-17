# Microsoft Agent Framework を使用して A2A [Agent-to-Agent] 対応 Agent を作成する

## 方法

1. Microsoft Agent Framework の A2A 用パッケージをインストールする

    ```bash
    pip install agent-framework-a2a
    ```

1. Agent Card の設定ファイル `.well-known/agent.json` を追加する

    [.well-known/agent.json](.well-known/agent.json)

    > A2A プロトコルでは、Agent Card の設定ファイルを `https://${base_url}/.well-known/agent.json` で公開する仕様になっている

1. A2A Agent のコードを実装する

    [run.py](run.py)

1. A2A Agent を使用したコードを実行する

    ```bash
    python run.py
    ```
