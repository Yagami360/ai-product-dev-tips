# 【Firebase】Firebase Hosting を使用して GKE 上の WebAPI からの出力を返す GUI 付きウェブアプリを作成する

## ■ 方法

1. GKE 上に WebAPI をデプロイする
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

1. FireBase を初期化し、静的な Web サイト `index.html` のテンプレートを作成する
    ```sh
    # Firebase へのログイン
    $ firebase login --project ${PROJECT_ID}

    # Firebase プロジェクトを初期化
    $ firebase init --project ${PROJECT_ID}
    ```

1. Cloud Storage for Firebase に `index.html` で利用する javascripts ファイルをアップロードする<br>
    左側のタブの「Storage」をクリックして「スタートガイド」ボタンをクリックするとダイアログが表示される。ダイアログに従って Cloud Storage 利用手続きを行うと、以降は Cloud Stogage の設定画面が表示されるので、「ファイルをアップロード」ボタンをクリックし、`index.html` で利用する javascripts ファイルをアップロードする<br>

    > [ToDO] CLI でこの作業を自動化する

1. Cloud Storage for Firebase に `index.html` で利用する css ファイルをアップロードする<br>
    同様にして、Cloud Stogage の設定画面から「ファイルをアップロード」ボタンをクリックし、`index.html` で利用する css ファイルをアップロードする<br>

    > [ToDO] CLI でこの作業を自動化する

1. Cloud Storage for Firebase にウェブサイト上で表示させたい画像をデータをアップロードする<br>
    同様にして、Cloud Stogage の設定画面から「ファイルをアップロード」ボタンをクリックし、画像データをアップロードする<br>

    > [ToDO] CLI でこの作業を自動化する
    
1. 静的な Web サイト `index.html` を作成する。<br>
    ```html
    ```

    `<script src=xxx></script>` や `<img src=xxx>` などで指定する各種リソース（javascript, css, 画像データ等）のパスには、上記 Cloud Storage for Firebase に保管したデータへのダウンロードURLを指定する。ダウンロードURLは、firebase storage のコンソール画面でアクセストークンをクリックすることで取得可能。
    <img src="https://user-images.githubusercontent.com/25688193/130308318-ee715eb5-e885-4475-bbae-159beef02dd2.png" width="500"><br>

    例えば、firebase storage のコンソール画面からアクセストークンをクリックすることで取得可能な ダウンロード URL を、`<img src="ダウンロードURL" id="xxx">` の src 属性に直接指定することで、firebase storage 上の画像を HTML で表示できる<br>

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

1. Firebase Hosting を利用して、作成した静的な Web サイト `index.html` をデプロイする
    ```sh
    # Firebase Hosting でウェブサイトをデプロイ
    $ firebase deploy --project ${PROJECT_ID}
    ```

1. Web サイトを表示する
    ```sh
    # Hosting URL を開く
    $ open https://${PROJECT_ID}.web.app
    ```

1. Web サイトの GUI を利用して出力画像を生成する
    1. GraphCut API サーバーの URL に GKE 上の Web-API の URL を設定する
    1. 人物画像を指定する
    1. 「背景除去画像を生成」ボタンをクリックし、出力画像を生成する
