# 【nginx】nginx での Webサーバーを https 化する（自己署名SSL認証書を使用する場合）
openssl を用いて作成した自己署名SSL認証書（オレオレ証明書）を、``


## ■ 使用法

1. openssl の設定
    1. `openssl` をインストール<br>
        1. Ubuntu の場合
            ```sh
            $ sudo apt install openssl
            ```
        1. Mac の場合
            ```sh
            $ sudo apt install openssl
            ```

    1. 秘密鍵（*.key）を作成<br>
        サーバー上で SSL 認証のための秘密鍵（*.key）を作成
        ```sh
        # パスワードあり時
        openssl genrsa -aes128 -out ${FILE_NAME}.key 2048
        ```
        - `-aes128` : 鍵の保護（AES-128）
        - `2048` : 鍵の長さ（2048 bit）

        ```sh
        # パスワードなし時
        openssl genrsa -out ${FILE_NAME}.key 2048
        ```

    1. 【省略可】公開鍵（*.key）を作成<br>
        秘密鍵から公開鍵（*.key）を作成する
        ```sh
        $ openssl rsa -in ${FILE_NAME}.key -pubout -out ${FILE_NAME}_public.key
        ```

    1. 証明書署名要求（*.csr）の作成<br>
        ```sh
        openssl req -new -key ${FILE_NAME}.key -out ${FILE_NAME}.csr
        ```
        - Country Name (2 letter code) : 国名（`JA` など）
        - Common Name (e.g. server FQDN or YOUR name) : SSL認証を行うサイト（`hoge.com` など）
            - `*` を含めたものにすると、ワイルドカード証明書になる。（例 : `*.com`）
            - `${IPアドレス}:${ポート番号}` の形式も指定可能？

    1. SSL証明書（*.crt）への署名<br>
        ```sh
        $ openssl x509 -req -days 3650 -in ${FILE_NAME}.csr -signkey ${FILE_NAME}.key -out ${FILE_NAME}.crt
        ```
        - `-days` : SSL認証書の有効期限

        作成したSSL証明書（*.crt）は、バイナリ形式であるが、以下のコマンドで中身の文字列を確認できる
        ```sh
        $ openssl x509 -text -in ${FILE_NAME}.crt
        ```

    1. Subject Alternative Name (SAN) で複数ホストに対応する<br>
        OpenSSLで作成するSSL証明書は、Common Name (CN) でひとつのホスト名に対してのみ有効になっているが、SAN（Subject Alternative Name）を使用すると複数のホスト名に対応させることができる。<br>
        最新の Chrome では、Common Name (CN) を判定せず、SAN で判定するようになっているので、SAN を設定しないで Chrome で https サイトにアクセスした場合は `NET::ERR_CERT_COMMON_NAME_INVALID` のエラーが発生してしまう。<br>
        そのため https 化したサイトの Chrome 対応を実現するためには SAN の設定は必須となる。<br>

        SAN は、以下の手順で設定可能。<br>
        1. 以下のような `${FILE_NAME}_san.txt` を作成する（ファイル名は任意）
            ```txt
            subjectAltName = DNS:*.com, IP:0.0.0.0
            ```
            - `DNS:` : APIサーバーのドメイン（ホスト名）を指定（複数可）
            - `IP:` : APIサーバーのIPアドレスを指定（複数可）

            ```sh
            # シェルスクリプトで txt ファイルを作成する場合
            $ touch ${FILE_NAME}_san.txt
            $ echo "subjectAltName = DNS:*.com, IP:0.0.0.0" > ${FILE_NAME}_san.txt
            ```
        1. `--extfile` に作成した `${FILE_NAME}_san.txt` を指定し、SSL証明書（*.crt）に著名
            ```sh
            $ openssl x509 -req -days 3650 -in ${FILE_NAME}.csr -signkey ${FILE_NAME}.key -out ${FILE_NAME}.crt -extfile ${FILE_NAME}_san.txt
            ```

1. nginx の設定
    1. nginx をインストールする<br>
        - MacOS の場合
            ```sh
            $ brew install nginx
            ```
        - Ubuntu の場合
            ```sh
            ```

    - https 通信への対応<br>
        https通信（SSL認証）に対応した Web サーバーを構築する場合は、`nginx.conf` の HTTP モジュールに以下のような設定を追加すれればよい
        ```conf
        http{
            server{
                listen 8080 ssl;                                # 8080 ポートとSSLを使うことを指定
                #ssl on;                                        # SSL（https通信）を有効化 | 最新の nginx では、listen ${PORT} ssl の指定のみで十分になった模様
                ssl_certificate      ../open_ssl/server.crt;    # SSL 証明書＋中間証明書のファイルパスを指定
                ssl_certificate_key  ../open_ssl/server.key;    # 秘密鍵のファイルパスを指定
            }
        }
        ```

    1. `nginx` コマンドで Nginx の Web サーバーを起動する<br>
        https 用に修正した `nginx.conf` を `-c` オプションで指定した以下のコマンドで Nginx の Web サーバーを起動する。
        ```sh
        $ nginx -c ${NGINX_CONF_FILE_PATH}
        ```

1. https 化した Web サーバーにブラウザアクセスする<br>
    「Welcome to nginx!」が表示されれば成功。<br>
    Chrome で `NET::ERR_CERT_INVALID` のエラーが発生する場合は、ページが選択されていることを確認して、`thisisunsafe` を入力すればよい

    - MacOS の場合
        ```sh
        # 8080 版ポートの場合
        $ open https://localhost:8080
        ```

## ■ 参考サイト
- https://qiita.com/riita10069/items/5d36dfeb756e3b6c4978#tls%E8%A8%BC%E6%98%8E%E6%9B%B8%E3%81%A8%E9%8D%B5%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%AE%E6%8C%87%E5%AE%9A
- https://qiita.com/morrr/items/7c97f0d2e46f7a8ec967#sslhttps%E3%81%AB%E5%AF%BE%E5%BF%9C%E3%81%99%E3%82%8B