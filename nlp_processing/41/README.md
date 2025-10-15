# Microsoft Agent Framework を使用して簡単なチャットを行う

## 方法

1. Microsoft Agent Framework をインストールする

    ```bash
    pip install agent-framework
    ```

1. Azure からリソース作成する

    - Azure OpenAPI で動かす場合

        <img width="800" alt="Image" src="https://github.com/user-attachments/assets/eac99545-adab-478a-a207-be193024e4a3" />

        [Azure OpenAPI] -> [モデルのデプロイ] の流れで作成

    - Azure AI Foundry で動かす場合

        xxx

1. 環境変数を設定する

    - Azure OpenAPI で動かす場合

        ```bash
        export AZURE_OPENAI_ENDPOINT="dummy"
        export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="dummy"
        export AZURE_OPENAI_API_KEY="dummy"
        ```

    - Azure AI Foundry で動かす場合

        ```bash
        export AZURE_AI_PROJECT_ENDPOINT="dummy"
        export AZURE_AI_MODEL_DEPLOYMENT_NAME="dummy"
        ```

1. Microsoft Agent Framework を使用したコードを実装する

    - Azure OpenAPI で動かす場合

        [agent.py](agent.py)

    - Azure AI Foundry で動かす場合

        xxx

1. Microsoft Agent Framework を使用したコードを実行する

    ```bash
    python agent.py
    ```

    回答

    ```bash
    もちろん！では、これをどうぞ：

    なぜコンピュータは冷たく感じるの？

    だって、いつもウィンドウを開けているから！
    ```

## 参考サイト

- Azure OpenAPI で動かす場合

    - https://learn.microsoft.com/ja-jp/agent-framework/tutorials/quick-start?pivots=programming-language-python

- Azure OpenAPI で動かす場合

    - https://zenn.dev/headwaters/articles/2d8222bf2214ad
