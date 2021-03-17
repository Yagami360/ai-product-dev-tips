# 【Flask】Flask での Web-API を https 化する（自己署名SSL認証書を使用する場合）
https のブラウザサイトから http の Web-API にアクセスする場合、https からは http の Web-API にアクセスできず Web-API を https 化する必要があるケースが存在する。<br>

http での Web-API を http -> https 化（SSL認証）したい場合は、openssl を用いて自己署名SSL認証書（オレオレ証明書）を作成し、https 化する方法がある。<br>

この際に、最新の Chrome では、Common Name (CN) を判定せず、Subject Alternative Name (SAN) で判定するようになっているので、SAN を設定しないで https サイトに Chrome でブラウザアクセスした場合は、以下の画面のような `NET::ERR_CERT_COMMON_NAME_INVALID` のエラーが出ることに注意。

<img src="https://user-images.githubusercontent.com/25688193/111427116-f39cf400-8738-11eb-95ad-eb3fbfb18175.png" width="300"><br>

SAN を設定し、更に Chrome の設定で作成したSSL認証（*.crt）を認証するように設定変更することで、自己署名SSL認証書（オレオレ証明書）使った https サイトに Chrome でブラウザアクセスした場合でも `NET::ERR_CERT_INVALID` エラーや `NET::ERR_CERT_COMMON_NAME_INVALID` エラーなしにうまく表示させることができる。

> SAN を設定しても自己署名SSL認証書（オレオレ証明書）を使っている限りは、各々のユーザーに Chrome 設定で作成したSSL認証（*.crt）の認証許可の処理を個別に行ってもらう必要がある。自己署名でない正式なSSL認証書（認証局[CA]を使用）を使わない限り、このの問題は解決しないことに注意

<!--
> - 自己署名SSL認証書（オレオレ証明書）<br>
> xxx
-->

## ■ 手順

### 1. openssl で自己署名SSL認証書（オレオレ証明書）を発行する
<img src="https://user-images.githubusercontent.com/25688193/111424521-3eb50800-8735-11eb-8bd2-1bc2efcadf44.png" width="500"><br>

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

### 2. Flask での API コードの https 対応
1. `app.py` 内の `app.run()` 呼び出し時に、作成した秘密鍵 `server.key` と `server.crt` から設定される `ssl_context` 引数を指定することで
    ```python
    import ssl
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(os.path.join(args.ssl_dir,'server.crt'), os.path.join(args.ssl_dir,'server.key'))
    app.run( host=args.host, port=args.port, ssl_context=context, threaded=False )
    ```

### 3. requsts モジュールでのリクエスト処理で `verify` を指定する

- `verify` 引数にSSL証明書（*.crt）のパスを指定<br>
    requests モジュールの `requests.post()` メソッドの `verify` 引数に、上記で作成したSSL証明書（*.crt）のパスを指定することで、https 化した Web-API からレスポンスを取得することができる。
    ```python
    import requests
    api_server_url = "https://localhost:5000/api_server"
    request_msg = { 'test_value' : 0 }
    request_msg = json.dumps(request_msg)
    try:
        api_responce = requests.post( api_server_url, json=request_msg, verify="api/open_ssl/server.crt" )
        api_responce = api_responce.json()
        if( args.debug ):
            print( "api_responce : ", api_responce )
    except Exception as e:
        print( "通信失敗 [API server]" )
        print( "Exception : ", e )
        exit()

    print( "api_responce[status] : ", api_responce["status"] )
    ```

- `verify=False` で指定する場合<br>
    `verify=False` を指定することで、SSL証明書（*.crt）に不備があっても https 化した Web-API にアクセスできる。但しこの場合に Chrome からブラウザアクセスした場合は、`NET::ERR_CERT_INVALID` のエラーが発生することに注意。
    ```python
    import requests
    api_server_url = "https://localhost:5000/api_server"
    request_msg = { 'test_value' : 0 }
    request_msg = json.dumps(request_msg)
    try:
        api_responce = requests.post( api_server_url, json=request_msg, verify=False )
        api_responce = api_responce.json()
        if( args.debug ):
            print( "api_responce : ", api_responce )
    except Exception as e:
        print( "通信失敗 [API server]" )
        print( "Exception : ", e )
        exit()

    print( "api_responce[status] : ", api_responce["status"] )
    ```

### 3. Chrome の設定
1. Chrome の「設定 -> プライバシーとセキュリティー -> 証明書の管理」を開く<br>
    <img src="https://user-images.githubusercontent.com/25688193/111436664-952a4280-8745-11eb-9e82-d42f0cd7a458.png" width="500"><br>
1. Mac の場合は、キーチェーンアクセスの画面が表示されるので、「新規のキーチェーン項目を作成します」ボタンをクリックし、作成した SSL証明書（*.crt）を選択する。<br>
    <img src="https://user-images.githubusercontent.com/25688193/111436893-d3276680-8745-11eb-8dcd-360eda709d78.png" width="500"><br>
1. 作成したキーチェーン項目をクリックし、信頼タブを展開し、SSL 項目を「常に信頼」に変更する<br>
    <img src="https://user-images.githubusercontent.com/25688193/111436323-2fd65180-8745-11eb-9252-b216d0c969d2.png" width="500"><br>
1. https 化した Web-API サーバーに Chrome でブラウザアクセスする<br>
    ```sh
    open https://${HOST}:${PORT}
    ```
    `NET::ERR_CERT_INVALID` や `NET::ERR_CERT_COMMON_NAME_INVALID` のエラーなしに表示された場合は、上記までの処理がうまくいっている。

## ■ 参考サイト
- https://kazuhira-r.hatenablog.com/entry/20180803/1533302929
- https://qiita.com/t-kuni/items/d3d72f429273cf0ee31e
- https://qiita.com/taka_katsu411/items/fb1ad876c0017b9fe49d
