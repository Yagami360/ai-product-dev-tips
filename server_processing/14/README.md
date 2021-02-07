# 【Firebase】Firebase Hosting を使用して静的なウェブサイトをデプロイする
Firebase Hosting を使用することで、Firebase を使用した静的なウェブサイト（HTML）を Hosting にデプロイし、公開することができる。

## 1. Firebase プロジェクトの作成
1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1)にアクセス
1. 「プロジェクトを作成」
1. 「設定」ボタン→「全般」タブから、GCP リソースのリージョンを指定する<br>
    <img src="https://user-images.githubusercontent.com/25688193/107106996-d4759180-6871-11eb-909c-14915bde83c6.png" width="500"><br>

## 2. ウェブアプリを Fisebase に登録する
1. Firebase コンソールの「プロジェクトの概要」ページの中央にあるウェブアイコン `</>` をクリックし、設定ワークフローを起動する。<br>
<img src="https://user-images.githubusercontent.com/25688193/107107327-bd37a380-6873-11eb-972d-4957992a748c.png" width="300"><br>
1. 設定ワークフロー画面でアプリ名を入力後、「アプリを登録」ボタンをクリックする。

## 3. Firebase Hosting でウェブサイトをデプロイし、公開する
1. npm のインストール<br>
    npm のインストールしていない場合は、npm をインストールする。<br>
    MacOS の場合、以下のコマンドでインストールできる
    ```sh
    # npm のインストール（MacOSの場合）
    $ brew install npm
    ```
    > - Node.js<br>
    > サーバサイドで JavaScript を実行するための仕組み

    > - npm (node package manager)<br>
    > Node.js のパッケージを管理するための CLI 

1. `package.json` を作成する<br>
    プロジェクトディレクトリ直下に、以下の `package.json` を作成する
    ```json
    {
    "name": "fire-app",
    "version": "1.0.0",
    "main": "index.js",
    "scripts": {
        "start": "node index.js",
        "test": "echo \"no test specified\" && exit 1"
    },
    "dependencies": {
        "firebase": "^5.8.2"
    }
    }
    ```
    または、以下のコマンドを実行し、`package.json` を作成する
    ```sh
    $ npm init
    ```

    > - `package.json`<br>
    > npm でインストールしたパッケージのバージョン情報を格納した json ファイル。この `package.json` からパッケージを一括でインストールすることが出来る

1. Firebase JavaScript SDK（`firebase` コマンド）をインストールする<br>
    作成した `package.json` を元に、Firebase JavaScript SDK（`firebase` コマンド）をインストールする
    ```sh
    # Firebase CLI のインストール
    $ sudo npm install -g firebase-tools
    ```
    - sudo コマンドなしだと、`/usr/local/lib/node_modules` ディレクトリ（`root`権限）へのアクセスエラーが発生することに注意

1. firebase にログインする
    ```sh
    $ firebase login
    ```

1.  Firebase プロジェクトを初期化
    ```sh
    $ firebase init
    ```
    
    コマンド実行後、以下の画面が表示されたら a キーを入力し、全ての機能を有効化
    <img src="https://user-images.githubusercontent.com/25688193/107134141-b328aa00-6932-11eb-9c20-60ab426ac8d6.png" width="500"><br>
    <img src="https://user-images.githubusercontent.com/25688193/107134213-6396ae00-6933-11eb-9e7a-7a06481351ed.png" width="300"><br>

    - その他の選択肢は、基本的にデフォルト設定でよい（yes or no の選択肢は、大文字 Y or N 側）
    - Firestore のデータベースを一度も作成してない場合は、[Firebase プロジェクトページ](https://console.firebase.google.com/project/sample-app-73cab/firestore) で先にデータベースを作成しておく必要があることに注意

    `firebase init` 実行後、以下のファイルとディレクトリが自動的に作成される。基本的には `public/` フォルダ内のファイルを触るだけで良い
    ```python
    + .firebase/                # デプロイによる実行内容に関しての情報。ユーザーが利用することはない
    + functions/                # Cloud Function に関しての各種ファイルを格納
    + public/                   # Web サイトとして公開される各種ファイルを格納
    + database.rules.json       # Realtime Database のセキュリティールール
    + firebase.json             # Firebase 各種機能設定ファイル
    + firestore.indexes.json    # Cloud Firestore のインデックス情報の設定ファイル
    + firestore.rules           # Cloud Firestore のセキュリティールール
    + storage.rules             # Storage のセキュリティールール
    ```

1. `public/index.html` の内容を必要に応じて書き換える<br>
    ウェブページ（HTML）で firebase の機能を利用する場合は、`public/index.html` 内に、以下のような firebase を読み込む `<script>` タグを埋め込む。
    ```html
    <!DOCTYPE html>
    <html lang="ja">
        <head>
        <meta charset="utf-8">
        <title>Sample Page</title>
        <script src="https://www.gstatic.com/firebasejs/5.8.4/firebase-app.js"></script>
        <script>
        var config = {
            apiKey: "……APIキー……",
            authDomain: "……AUTHドメイン……",
            databaseURL: "……データベース……",
            projectId: "……プロジェクトID……",
            storageBucket: "……ストレージ……",
            messagingSenderId: "……メッセージID……"
        };
        var fbase;
        try {
            fbase = firebase.initializeApp(config);
        } catch(e) {
            console.log(e);
        }
        console.log(fbase.name);
        </script>
    </head>
    <body>
        <h1>Sample Page</h1>
        <p>Firebase name: 
            <script>
            document.write(fbase.name);
            </script>
        </p>
    </body>
    </html>
    ```

1.  ウェブサイトをデプロイする<br>
    以下のコマンドでウェブサイト（`public/index.html`）を Hosting にデプロイして、公開する。
    ```sh
    $ firebase deploy
    ```
    ```sh
    # public/ 以下のみデプロイする場合
    $ firebase deploy --only hosting
    ```
    - [Firebase のプラン](https://console.firebase.google.com/project/sample-app-73cab/usage/details)を Blaze（従量制）にしておく必要があることに注意

    コマンド実行時に、以下のエラー
    ```sh
    Error: Parse Error in remoteconfig.template.json:

    No data, empty input at 1:1

    ^
    File: "remoteconfig.template.json"
    ```
    が発生する場合は、`firebase.json` 内の以下の部分を削除すればよい
    ```json
    "remoteconfig": {
        "template": "remoteconfig.template.json"
    }
    ```

1. ウェブサイトの URL にアクセスする<br>
    ```sh
    $ open https://${PROJECT_ID}.web.app
    ```
    <img src="https://user-images.githubusercontent.com/25688193/107134796-ae66f480-6938-11eb-9682-ae3ca5d0654a.png" width="500"><br>


## ■ 参考サイト
- https://firebase.google.com/docs/web/setup?hl=ja
- https://www.sejuku.net/blog/86468 
- https://codezine.jp/article/detail/11103
- https://qiita.com/alingogo/items/100e6c62d849058e89f9
