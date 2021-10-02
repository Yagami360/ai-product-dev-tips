# 【Firebase】Firebase Hosting と Firebase Cloud Function を使用して GKE 上の http 通信での WebAPI からの出力を返す GUI 付きウェブアプリを作成する（リバースプロキシとしての cloud function 経由で API を呼び出す）

Web アプリ上から外部の API を呼び出す際は、https 通信である必要がある。そのため https 化されていない GKE 上の Web-API を Web アプリ上から呼び出すことができないという問題がある。

GKE 上の Web-API を https 化することでもこの問題は解決できるが、一般的に https 化するは少々面倒な手続きが必要になる。

ここでは、firebase cloud function に https 通信 -> http 通信へのリバースプロキシとして役割をさせることで、GKE 上の Web-API を https 化することなく、手軽に Web アプリ上から外部の http 通信での API を呼び出す方法を記載する


<img src="https://user-images.githubusercontent.com/25688193/135239832-fcb39288-587b-475f-83d9-18753cb937f2.png" width="500"><br>

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

1. FireBase を初期化し、静的な Web サイト `index.html` と Cloud Function `index.js` のテンプレートを作成する
    ```sh
    # Firebase へのログイン
    $ firebase login --project ${PROJECT_ID}

    # Firebase プロジェクトを初期化
    $ firebase init --project ${PROJECT_ID}
    ```

    > `Firebase Hosting` と `Cloud Functions for Firebase` の機能を有効にして初期化する

1. `public` ディレクトリ以下に、静的なウェブサイト `index.html` を作成する
    ```html
    ```

1. Cloud Function `index.js` にリクエスト処理を行う javascript を作成する<br>
    `index.js` で定義した firebase cloud function を利用して、API にリクエスト処理を行う javascript `js/request.js` を作成する。このスクリプトは、静的なウェブサイト `index.html` から呼び出される
    - `js/request.js`
        ```python
        ```

    - `js/utils.js`
        ```python
        ```

1. `public` ディレクトリ以下に、静的なウェブサイト `index.html` で利用する各種リソースのファイルを保管する<br>
    `public` ディレクトリ以下 に `index.html` で利用する各種リソースのファイル（javascript, css, 画像データ等）を保管する

1. `functions` ディレクトリ以下に、firebase cloud functionhttps 通信 -> http 通信へのリバースプロキシとして役割を行う `index.js` を作成する。<br>
    `functions` ディレクトリ以下に、https 通信 -> http 通信へのリバースプロキシとして役割を行う firebase cloud function `index.js` を作成する。
    ```javascript
    ```

    > Node.js において、定義した関数を外部から使用可能にするためには、`exports.${関数名} = functions` の形式で定義する必要がある。

    > この cloud function へのリクエスト処理は、`js/request.js` 内にて、cloud function の URL `https://${ZONE}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}` から行う

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

1. firebase cloud function `index.js` で追加使用する各種モジュールをインストールする
    ```sh
    $ cd functions
    $ npm install --save request request-promise
    $ ..
    ```

1. Firebase Hosting を利用して、作成した静的な Web サイト `index.html` と firebase cloud function `index.js` をデプロイする
    ```sh
    $ firebase deploy --project ${PROJECT_ID}
    ```

    > 「Firebase のプラン」を Blaze（従量制）にしておく必要があることに注意

1. Web サイトを表示する
    ```sh
    # Hosting URL を開く
    $ open https://${PROJECT_ID}.web.app
    ```

1. Web サイトの GUI を利用して出力画像を生成する
    1. 「GraphCut API サーバーの URL を指定」に、GKE 上の Web-API の URL `http://${HOST}:5000` を設定する
    1. 「Firebase Cloud Function の URL を指定」に、Cloud Function の URL `https://${ZONE}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}` を設定する
    1. 人物画像を指定する
    1. 「背景除去画像を生成」ボタンをクリックし、出力画像を生成する

1. 【オプション】Cloud Function のログデータを確認する
    - CLI を使用する場合
        ```sh
        $ firebase functions:log --only ${FUNCTION_NAME}
        ```

    - GUI を使用する場合
        ```sh
        $ open https://console.firebase.google.com/project/${PROJECT_ID}/functions/logs?hl=ja&functionFilter=${FUNCTION_NAME}(${ZONE})&search=&severity=DEBUG
        ```

1. 【オプション】WebAPI のログデータを確認する
    - コンテナログの確認
        ```sh
        $ kubectl logs `kubectl get pods | grep "graph-cut-api-pod" | awk '{print $1}'` graph-cut-api-container
        ```

    - API ログファイルの確認
        ```sh
        $ kubectl exec -it `kubectl get pods | grep "graph-cut-api-pod" | awk '{print $1}'` /bin/bash
        $ cat log/app.log
        ```