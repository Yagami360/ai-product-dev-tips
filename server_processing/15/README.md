# 【Firebase】Firebase Cloud Function を使用して動的なウェブアプリをデプロイする
Firebase の Cloud Function 機能を使用することで、Node.js 使用した動的なウェブアプリを Hoisting にデプロイし、公開することができる。

## 1. Firebase プロジェクトの作成
1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1)にアクセス
1. 「プロジェクトを作成」
1. 「設定」ボタン→「全般」タブから、GCP リソースのリージョンを指定する<br>
    <img src="https://user-images.githubusercontent.com/25688193/107106996-d4759180-6871-11eb-909c-14915bde83c6.png" width="500"><br>

## 2. ウェブアプリを Fisebase に登録する
1. Firebase コンソールの「プロジェクトの概要」ページの中央にあるウェブアイコン `</>` をクリックし、設定ワークフローを起動する。<br>
<img src="https://user-images.githubusercontent.com/25688193/107107327-bd37a380-6873-11eb-972d-4957992a748c.png" width="300"><br>
1. 設定ワークフロー画面でアプリ名を入力後、「アプリを登録」ボタンをクリックする。

## 3. Firebase を使用した動的なウェブアプリ（Node.js 使用）をデプロイする

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

    `firebase init` 実行後、以下のファイルとディレクトリが自動的に作成される。functions ディレクトリを
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

1. `functions/index.js` の内容を必要に応じて書き換える<br>
    動的な Node.js プログラム `functions/index.js` の内容を必要に応じて書き換える。
    ```js
    const functions = require("firebase-functions");

    // // Create and Deploy Your First Cloud Functions
    // // https://firebase.google.com/docs/functions/write-firebase-functions
    //
    exports.helloWorld = functions.https.onRequest((request, response) => {
        functions.logger.info("Hello logs!", {structuredData: true});
        response.send("Hello from Firebase!");
    });
    ```

1.  動的なウェブアプリをデプロイする<br>
    以下のコマンドで動的なウェブアプリ（`functions/index.js`）を Hosting にデプロイして、公開する
    ```sh
    $ firebase deploy 
    ```
    ```sh
    # functions/ ディレクトリのみデプロイする場合
    $ firebase deploy --only functions
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

1. Clould Function の URL にアクセスする<br>
    ```sh
    $ open https://${ZONE}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}
    ```
    ```sh
    # 例
    $ open https://us-central1-sample-app-73cab.cloudfunctions.net/helloWorld
    ```
    <img src="https://user-images.githubusercontent.com/25688193/107136240-d5c3be80-6944-11eb-91c7-17a4fbc74447.png" width="500"><br>


## ■ 参考サイト
- https://www.sejuku.net/blog/86468