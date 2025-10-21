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

1. その他 LangChain パッケージをインストールする

    ```bash
    pip install -U langchain-google-genai
    ```

1. xxx

    ```bash
    langgraph new a2a-agent --template new-langgraph-project-python
    ```

1. LangGraph API を使用した A2A 対応 AI Agent のコードを実装する

    [agent.py](agent.py)

    ポイントは、以下の通り

    - xxx

1.  LangGraph Server を起動する

    LangGraph CLI コマンド `langgraph` で起動する

    ```bash
    langgraph dev
    ```

## 参考サイト

- https://docs.langchain.com/langsmith/server-a2a
