# 【Firebase】Firebase のデプロイ処理（ウェブアプリ）
Firebase JavaScript SDK を使用することで、ウェブアプリ（JavaScript）に Firebase をデプロイすることができる。

## ■ Firebase のウェブアプリへのデプロイ手順

1. Firebase プロジェクトの作成
    1. [Firebase コンソール画面](https://console.firebase.google.com/?hl=ja&pli=1)にアクセス
    1. 「プロジェクトを作成」
    1. 「設定」ボタン→「全般」タブから、GCP リソースのリージョンを指定する<br>
        <img src="https://user-images.githubusercontent.com/25688193/107106996-d4759180-6871-11eb-909c-14915bde83c6.png" width="500"><br>
1. ウェブアプリを Fisebase に登録する<br>
    1. Firebase コンソールの「プロジェクトの概要」ページの中央にあるウェブアイコン `</>` をクリックし、設定ワークフローを起動する。<br>
    <img src="https://user-images.githubusercontent.com/25688193/107107327-bd37a380-6873-11eb-972d-4957992a748c.png" width="300"><br>
    1. 設定ワークフロー画面でアプリ名を入力後、「アプリを登録」ボタンをクリックする。
1. Firebase SDK を追加して Firebase を初期化する
    1. Firebase Hosting 使用時
        xxx        
    1. Node.js 使用時
        以下のコマンドで、Firebase JavaScript SDK をインストールする
        ```sh
        # package.json ファイルがない場合は、JavaScript プロジェクトのルートから次のコマンドを実行して作成します。
        $ npm init
        ```
        ```sh
        # firebase npm パッケージをインストールし、package.json ファイルに保存
        $ npm install --save firebase
        ```
        ```sh
        # CLI のインストール
        $ npm install -g firebase-tools
        ```


> - Firebase Hosting<br>
> xxx

> - Node.js<br>
> xxx

## ■ 参考サイト
- https://firebase.google.com/docs/web/setup?hl=ja
- https://qiita.com/alingogo/items/100e6c62d849058e89f9