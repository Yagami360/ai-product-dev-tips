# Dify をローカル環境（オンプレ環境）で起動する

## 使用方法

1. Dify の GitHub リポジトリからソースコードをクローンする
    ```bash
    git clone https://github.com/langgenius/dify.git
    cd dify
    ```

1. 【オプション】Dify の Docker コンテナ 用環境変数を設定する
    ```bash
    cd docker
    cp .env.example .env
    ```

    `.env.example` では、API_URL 等の様々な環境変数の値を設定できるようになっている

    <details>
    <summary>.env.example</summary>

    ```
    ...
    # ------------------------------
    # Common Variables
    # ------------------------------

    # The backend URL of the console API,
    # used to concatenate the authorization callback.
    # If empty, it is the same domain.
    # Example: https://api.console.dify.ai
    CONSOLE_API_URL=

    # The front-end URL of the console web,
    # used to concatenate some front-end addresses and for CORS configuration use.
    # If empty, it is the same domain.
    # Example: https://console.dify.ai
    CONSOLE_WEB_URL=

    # Service API Url,
    # used to display Service API Base Url to the front-end.
    # If empty, it is the same domain.
    # Example: https://api.dify.ai
    SERVICE_API_URL=

    # WebApp API backend Url,
    # used to declare the back-end URL for the front-end API.
    # If empty, it is the same domain.
    # Example: https://api.app.dify.ai
    APP_API_URL=

    # WebApp Url,
    # used to display WebAPP API Base Url to the front-end.
    # If empty, it is the same domain.
    # Example: https://app.dify.ai
    APP_WEB_URL=

    # File preview or download Url prefix.
    # used to display File preview or download Url to the front-end or as Multi-model inputs;
    # Url is signed and has expiration time.
    FILES_URL=
    ...
    ```

    </details>

    > `.env` でAPI_URL 等の値を適切に設定すれば、Dify 側に機密情報（ユーザー情報など）を API 経由で渡すことなく、Dify を利用することができる？

1. Dify の Docker コンテナを起動する
    ```bash
    docker compose up
    ```

1. ローカル環境で起動した Dify にアクセスする
    ブラウザで `http://localhost/install` にアクセスする
    ```sh
    open http://localhost/install
    ```

    ブラウザアクセスすると、以下のようなページが表示されるので、ユーザー名とパスワードを入力し管理者ユーザーを作成する<br>
    <img width="300" alt="image" src="https://github.com/user-attachments/assets/92072a7e-d2bd-4bcd-b086-77e1bce3fccf">


    > ローカル環境で動かしているので、Dify Cloud のユーザーとは別のユーザー管理になる

    その後、以下のようなログインページ（`http://localhost/signin`）に自動的にジャンプされるので、先ほど作成したユーザー名とパスワードでログインする<br>
    <img width="500" alt="image" src="https://github.com/user-attachments/assets/fe63b428-f224-4d8c-9d23-891889989ce5">

1. ローカル環境で起動した Dify コンソール UI から LLM アプリケーションを作成する<br>
    ログイン完了後、Dify コンソール UI にアクセスできるので、「[Dify の基本的な使い方（ワークフローを使用した LLM アプリケーションを作成する）](https://github.com/Yagami360/ai-product-dev-tips/tree/master/nlp_processing/20)」に従って、Dify を使用した LLM アプリケーションのワークフローを作成する<br>
    <img width="800" alt="image" src="https://github.com/user-attachments/assets/c7a462e0-14b6-4b2b-80ac-2959b5e1f139">


## 参考サイト

- https://github.com/langgenius/dify?tab=readme-ov-file#quick-start
