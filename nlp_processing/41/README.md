# Microsoft Agent Framework を使用して簡単なチャットを行う

## 方法

### 事前準備

1. Microsoft Agent Framework をインストールする

    ```bash
    pip install agent-framework
    ```

### Azure OpenAPI で動かす場合

1. Azure の Azure OpenAPI からリソース作成する

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/eac99545-adab-478a-a207-be193024e4a3" />

    [Azure OpenAPI] -> [モデルのデプロイ] の流れで作成

1. 環境変数を設定する

    ```bash
    export AZURE_OPENAI_ENDPOINT="dummy"
    export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="dummy"
    export AZURE_OPENAI_API_KEY="dummy"
    ```

1. Microsoft Agent Framework を使用したコードを実装する

    [run.py](run.py)

1. Microsoft Agent Framework を使用したコードを実行する

    ```bash
    python run.py
    ```

    回答

    ```bash
    もちろん！では、これをどうぞ：

    なぜコンピュータは冷たく感じるの？

    だって、いつもウィンドウを開けているから！
    ```


### Azure AI Foundry で動かす場合

1. Azure CLI をインストールする

    ```bash
    pip install azure-cli
    ```

    ```bash
    az --version
    ```

1. Azure の Azure AI Foundry からリソース作成する

    xxx

1. 環境変数を設定する

    ```bash
    export AZURE_AI_PROJECT_ENDPOINT="dummy"
    export AZURE_AI_MODEL_DEPLOYMENT_NAME="dummy"
    ```

1. azure コマンドで Azure に接続する

    ```bash
    az login
    ```

1. Microsoft Agent Framework を使用したコードを実装する

    xxx

## 参考サイト

- Azure OpenAPI で動かす場合

    - https://learn.microsoft.com/ja-jp/agent-framework/tutorials/quick-start?pivots=programming-language-python

- Azure OpenAPI で動かす場合

    - https://zenn.dev/headwaters/articles/2d8222bf2214ad
