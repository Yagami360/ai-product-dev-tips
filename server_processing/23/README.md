# 【nginx】nginx での Webサーバーを https 化する（自己署名SSL認証書を使用する場合）
openssl を用いて作成した自己署名SSL認証書（オレオレ証明書）を、``


## ■ 使用法

1. openssl をインストール
1. xxx
1. nginx をインストールする<br>
    - MacOS の場合
        ```sh
        $ brew install nginx
        ```
    - Ubuntu の場合
        ```sh
        ```
- https 通信への対応<br>
    https通信（SSL認証）に対応した Web サーバーを構築する場合は、`nginx.conf` のHTTP モジュールを以下のように設定すればよい
    ```conf
    http{
        listen 8080 ssl;                            # 80 ポートとSSLを使うことを指定
        ssl on;                                     # SSL（https通信）を有効化
        ssl_certificate      /path/to/cert.pem;     # SSL 証明書＋中間証明書のファイルパスを指定
        ssl_certificate_key  /path/to/cert.key;     # 秘密鍵のファイルパスを指定
    }
    ```
1. `nginx` コマンドで Nginx の Web サーバーを起動する
    ```sh
    $ nginx
    ```
    デフォルトでは、8080 版ポート

1. Web サーバーにブラウザアクセスする<br>
    ```sh
    # 8080 版ポートの場合
    $ open http://localhost:8080
    ```
    「Welcome to nginx!」が表示されれば成功
