# Web サーバーの基礎事項

## WebSocket 通信

双方向のHTTPプロトコルで、クライアントとサーバー間でリアルタイム通信を行うための技術。<br>

- HTTPとは異なり、`ws://` あるいは `wss://` から始まる。<br>
- クライアントとサーバ間の接続はどちらか一方が切断されると終了する<br>
- リアルタイムで更新が必要なアプリケーション（チャットアプリ等）で有用になる

<!--
- ヘッダー
    - Upgradeヘッダ : HTTPからWebSocketへのプロトコルのアップグレード
    - Connectionヘッダが存在する事で、この二つでHTTPからWebSocketへのプロトコルのアップグレードを表現している。アップグレードって言われると良く分からないけど、ただのHTTPでないんだって事をサーバーに伝えたいんだなーくらいに思っておけばOK。

- フレーム<br>
-->

## HTTP クッキー（Cookie）<br>

<img width="577" alt="image" src="https://github.com/Yagami360/ai-product-dev-tips/assets/25688193/54f3d0b5-12d0-4c31-b09b-67912ebe3173"><br>
サーバーがユーザーのウェブブラウザーに送信する小さなデータであり、ブラウザーに保存され、その後のリクエストと共に同じサーバーへ返送される。

## SSL/TLS 通信

<img width="800" alt="image" src="https://github.com/user-attachments/assets/986378de-3811-44ce-b1d9-03b8751d1f18" />

インターネット上の HTTP 通信を暗号化するプロトコルで、秘密鍵と認証局（CA）が発行した SSL証明書を使用して通信を暗号化する。HTTPS では、SSL/TLS 通信を使用している。（HTTPS = HTTP + SSL/TLS）<br>

- SSL/TLS 通信の流れ<br>
    SSL/TLS 通信の具体的な処理の流れは、以下のようになる。

    - SSL証明書の登録プロセス
        1. 管理者が SSL 認証のための秘密鍵（.key）を作成する
        1. 【省略可】管理者が 秘密鍵から公開鍵（.key）を作成する
        1. 管理者が SSL 証明書署名要求（*.csr）を作成する証明機関（CA）に送信する
        1. 証明機関（CA）が証明書（*.crt）を作成し、管理者に送信する
        1. 管理者が SSL証明書（*.crt）と秘密鍵（.key）をサーバーにインストールする

    - SSL/TLS 通信のプロセス
        1. クライアント（ブラウザ）がサーバーに接続要求
        1. サーバーが SSL 証明書（*.crt）を送信
        1. クライアント（ブラウザ）が SSL 証明書（*.crt）を検証
        1. クライアント（ブラウザ）がサーバーに接続要求
        1. （秘密鍵とSSL証明書を使用して）暗号化通信を確立する

- 証明機関（CA）<br>
    証明機関（CA）は、SSL証明書の発行を行う第３者機関。具体的には、以下のような機関がある。
    - Amazon Certificate Manager
    - Google Cloud Certificate Manager
    - Let's Encrypt

- SSL 証明書<br>
    SSL証明書は、SSL/TLS通信を実現するためのデジタル証明書であり、証明機関（CA）が発行する。

    - 自己署名SSL認証書（オレオレ証明書）
        認証局（CA）を介さずに、自分で作成する証明書。テスト用に使用される。
        <img width="700" alt="image" src="https://github.com/user-attachments/assets/51ad43ec-8063-49b7-9925-b16cfbb8a07b" />

## 参考サイト
- WebSocket
    https://qiita.com/south37/items/6f92d4268fe676347160