# 【Firebase】Firebase のデプロイ処理（ウェブアプリ）
Firebase JavaScript SDK を使用することで、ウェブアプリ（JavaScript）に Firebase をデプロイすることができる。

## 1. Firebase プロジェクトの作成
1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1)にアクセス
1. 「プロジェクトを作成」
1. 「設定」ボタン→「全般」タブから、GCP リソースのリージョンを指定する<br>
    <img src="https://user-images.githubusercontent.com/25688193/107106996-d4759180-6871-11eb-909c-14915bde83c6.png" width="500"><br>

## 2. ウェブアプリを Fisebase に登録する
1. Firebase コンソールの「プロジェクトの概要」ページの中央にあるウェブアイコン `</>` をクリックし、設定ワークフローを起動する。<br>
<img src="https://user-images.githubusercontent.com/25688193/107107327-bd37a380-6873-11eb-972d-4957992a748c.png" width="300"><br>
1. 設定ワークフロー画面でアプリ名を入力後、「アプリを登録」ボタンをクリックする。

## 3. ウェブアプリで Firebase を利用する。

### 3-1. HTML ファイル内に `<script>` タグを埋め込む（Firebase Hosting を使用）
ウェブページ（HTML）で、Firebase を利用する場合の方法は、以下のリンク先を参照

- [【Firebase】Firebase Hosting でのウェブサイトのデプロイ処理](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/14)

### 3-2. Node.js 使用時

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

1. firebase npm パッケージを一括インストール<br>
    作成した `package.json` を元に、以下のコマンドで firebase npm パッケージを一括でインストールする
    ```sh
    # `package.json`から firebase npm パッケージを一括でインストール
    $ sudo npm install --save firebase
    ```
    - sudo コマンドなしだと、`/usr/local/lib/node_modules` ディレクトリ（`root`権限）へのアクセスエラーが発生することに注意

1. `index.js` を作成する<br>
    JavaScript のエントリーポイント `index.js` を作成する。<br>
    `index.js` の内容は、例えば以下のような内容になる。
    ```js
    const http = require('http');
    const hostname = '127.0.0.1';
    const port = 3000;
    const firebase = require("firebase");

    let config = {
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

    const server = http.createServer(
            (req, res) => {
        res.statusCode = 200;
        res.setHeader('Content-Type', 'text/html');
        res.write('<html><body><h1>Firebase</h1>');
        res.write('<p>Database name: ' + fbase.name + '</p>');
        res.end('</body></html>\n');
    });

    server.listen(port, hostname, () => {
        console.log(`Server running at http://${hostname}:${port}/`);
    });
    ```

1. `index.js` を起動<br>
    以下のコマンドで、`index.js` に記載したプログラムを開始する
    ```sh
    $ npm run start
    ```

## ■ 参考サイト
- https://firebase.google.com/docs/web/setup?hl=ja
- https://qiita.com/taketakekaho/items/52b7c196ddbd4cb3c968