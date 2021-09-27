# 【Firebase】Firebase Hosting と Firebase Cloud Function を使用して GKE 上の http 通信での WebAPI からの出力を返す GUI 付きウェブアプリを作成する（リバースプロキシとしての cloud function 経由で API を呼び出す）

## ■ 方法

1. GKE 上に http 通信での WebAPI をデプロイする
    ```sh
    $ deploy_api_gke.sh
    ```

1. FireBase プロジェクトを作成する
    FireBase のコンソール画面から新規の FireBase プロジェクトを作成する

1. FireBase プロジェクトのデフォルトリージョンを設定する
    FireBase のコンソール画面から新規の FireBase プロジェクトを作成する

1. npm と Firebase CLI をインストールする
    ```sh
    # npm のインストール（MacOSの場合）
    $ brew install npm

    # Firebase CLI のインストール
    $ sudo npm install -g firebase-tools
    ```

1. FireBase を初期化し、動的な Web サイト `index.js` のテンプレートを作成する
    ```sh
    # Firebase へのログイン
    $ firebase login --project ${PROJECT_ID}

    # Firebase プロジェクトを初期化
    $ firebase init --project ${PROJECT_ID}
    ```

1. `functions` ディレクトリ以下 に `index.js` で利用する各種リソースのファイルを保管する<br>
    `functions` ディレクトリ以下 に `index.js` で利用する各種リソースのファイル（javascript, css, 画像データ等）を保管する

1. 動的な Web サイト `index.js` を作成する。<br>
    ```html
    ```

1. API にリクエスト処理を行う javascript を作成する<br>
    jQuery での Ajax 通信を利用して、API にリクエスト処理を行う javascript を作成する
    - `js/request.js`
        ```python
        ```

    - `js/utils.js`
        ```python
        ```

<!--
1. CORS [Cross-Origin Resource Sharing] の設定を行う。<br>
    デフォルトでは、設定されているドメイン以外からのアクセスが制限されているので、CORS [Cross-Origin Resource Sharing] の設定を行い、Web サーバー側に外部からのアクセスを許可するように変更する。

    1. CORS 設定ファイル `cors.json` （ファイル名は任意）を作成する
        ```json
        [
            {
                "origin": ["https://${PROJECT_ID}.firebaseapp.com", "http://localhost:5000"],
                "responseHeader": ["*"],
                "method": ["GET", "PUT", "POST", "DELETE"],
                "maxAgeSeconds": 3600
            }
        ]
        ```
        - `https://${PROJECT_ID}.firebaseapp.com` : Web アプリの公開 URL

    1. CORS 設定ファイル `cors.json` を Web アプリにデプロイする
        ```sh
        $ gsutil cors set cors.json gs://${PROJECT_ID}.appspot.com
        ```
        - `gs://${PROJECT_ID}.appspot.com` : Cloud Storage のパケット URL

        正しくデプロイできたかは、以下のコマンドで確認できる。
        ```sh
        $ gsutil cors get gs://${PROJECT_ID}.appspot.com 
        ```
-->

1. Firebase Hosting を利用して、作成した動的な Web サイト `index.js` をデプロイする
    ```sh
    # Firebase Hosting でウェブサイトをデプロイ
    $ firebase deploy --project ${PROJECT_ID}
    ```
    ```sh
    # functions/ ディレクトリのみデプロイする場合
    $ firebase deploy --project ${PROJECT_ID} --only functions
    ```

    > 「Firebase のプラン」を Blaze（従量制）にしておく必要があることに注意

1. Web サイトを表示する
    ```sh
    # Hosting URL を開く
    $ open https://${PROJECT_ID}.web.app
    ```
    ```sh
    $ open https://${ZONE}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}
    ```

1. Web サイトの GUI を利用して出力画像を生成する
    1. GraphCut API サーバーの URL に GKE 上の Web-API の URL を設定する
    1. 人物画像を指定する
    1. 「背景除去画像を生成」ボタンをクリックし、出力画像を生成する

