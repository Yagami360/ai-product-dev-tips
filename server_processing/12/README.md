# 【Firebase】Firebase の基礎事項
Google が提供しているウェブアプリ・iOS・アンドロイド向けの BaaS [Backend as a Service] で、サーバを用意せず、全てのバックエンド処理をクラウド環境（＝サーバレス）で実行できる。

Firebase を導入することで、主に以下のようなメリットが享受できる

- サーバレスの仕組みなので、サーバの環境構築や運用といった面倒な処理を自分で行うが必要なく、インフラの知識がなくてもサービス提供ができるようになる
- 認識機能を自作する必要がない
- 安い料金で利用することができる（基本的なプランなら無料）

## Firebase の主要機能

- Firebase Authentication<br>
    Firebase でのユーザー認証機能。<br>
    Goole アカウントや Twitter アカウントなどの各種ソーシャルサービスでのログイン機能もサポートされている

- Firebase Hosting<br>
    ウェブサイト（HTML）のホスティングを行う機能。<br>
    Firebase Hosting を使うことで、静的なウェブサイト（HTML）を Hosting にデプロイして公開することができる

- Cloud Functions for Firebase<br>
    Firebase で使う Cloud Functions 機能。<br>
    Cloud Functions を使うことで、機能を使用することで、Node.js 使用した動的なウェブアプリを Hoisting にデプロイし、公開することができる。 

- Database<br>
    - Realtime Database<br>
        NoSQL [Not only SQL] と呼ばれる SQL 言語を使わずにデータ操作ができるデータベースで、以前から使われていたデータベース

    - Cloud Firestore<br>
        NoSQL [Not only SQL] と呼ばれる SQL 言語を使わずにデータ操作ができるデータベースで、 最近追加されたデータベース

- Storage<br>
    Firebase で使うストレージ機能

## ■ 参考サイト
- https://firebase.google.com/docs/guides?hl=ja
