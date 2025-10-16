# Microsoft Agent Framework のワークフローを使用してマルチ Agent での処理を行う

<img width="606" height="510" alt="Image" src="https://github.com/user-attachments/assets/970a94c9-eed4-494f-9fe7-645186dba991" />

## 方法

### 事前準備

1. Microsoft Agent Framework をインストールする

    ```bash
    pip install agent-framework
    ```

1. ワークフロー可視化のための graphviz をインストールする

    - Ubuntu の場合

        ```bash
        sudo apt-get install graphviz
        ```

    - Mac OS の場合

        ```bash
        brew install graphviz
        ```

    - conda を使用する場合

        ```bash
        conda install -c conda-forge graphviz python-graphviz
        ```

### Azure AI Foundry で動かす場合

1. Azure CLI をインストールする

    ```bash
    pip install azure-cli
    ```

    ```bash
    az --version
    ```

1. Azure から Azure AI Foundry のリソース作成する

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/932ade27-6c9d-4979-9a72-8d282072b655" />

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/39643448-3e35-4590-8f7c-15f753045c84" />

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/84f70691-9095-418b-a389-efebd2ce0868" />

    1. [Azure AI Foundry] -> [リソースの作成]

    1. 作成したリソース画面にて、[モデルカタログ] -> [このモデルを使用する] の流れで作成

<!--
    1. 作成したリソース画面にて、[エージェント] -> [モデルをデプロイする] の流れで作成

    <img width="800" alt="Image" src="https://github.com/user-attachments/assets/dfaaa631-6659-4e45-8fad-3d85a9a98c25" />
-->

1. 環境変数を設定する

    ```bash
    export AZURE_AI_PROJECT_ENDPOINT="dummy"
    export AZURE_AI_MODEL_DEPLOYMENT_NAME="dummy"
    ```

    - `AZURE_AI_PROJECT_ENDPOINT`: Azure AI Foundry のプロジェクトエンドポイント（モデルエンドポイントではない）

        <img width="500" alt="Image" src="https://github.com/user-attachments/assets/71498b76-657f-47a2-9b68-d1cb67d5ed4d" />

1. azure コマンドで Azure に接続する

    ```bash
    az login
    ```

1. Microsoft Agent Framework を使用したコードを実装する

    [run.py](run.py)

    ポイントは、以下の通り

    - 以下の２つの AI Agent から構成されるマルチエージェントシステムのワークフローになっている

        - Writer の AI Agent
            - プロンプトでコンテンツライターと指示しただけの簡単な AI Agent

        - Reviewer の AI Agent
            - プロンプトでコンテンツレビュワーと指示しただけの簡単な AI Agent

1. Microsoft Agent Framework を使用したコードを実行する

    ```bash
    python run.py
    ```

    ```bash
    input_prompt:  手頃な価格で運転が楽しい新しい電動SUVのキャッチコピーを作成してください。
    Writer: 「手頃な価格で走りの楽しさ、電動SUVの新時代が始まる！」
    Reviewer: 「手頃な価格で魅力満点、電動SUVで新しいドライブ体験を！」
    ===== Final output =====
    「手頃な価格で魅力満点、電動SUVで新しいドライブ体験を！」
    ```

    複数の AI Agent で最終的な回答を出力するマルチエージェントシステムになっていることがわかる

    ```mermaid
    flowchart TD
        Writer["Writer (Start)"];
        Reviewer["Reviewer"];
        Writer --> Reviewer;
    ```

## 参考サイト

- https://learn.microsoft.com/ja-jp/agent-framework/overview/agent-framework-overview
- https://learn.microsoft.com/ja-jp/agent-framework/tutorials/workflows/agents-in-workflows?pivots=programming-language-python
- https://learn.microsoft.com/ja-jp/agent-framework/tutorials/workflows/visualization