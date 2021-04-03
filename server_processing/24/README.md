# 【nginx】nginx をリバースプロキシとして利用する
Nginx は、単一の Web サーバーとしての機能させるだけでなく、クライアントとサーバの通信の間に入って分散負荷等を行うリバースプロキシとして機能させることもできる。

> - リバースプロキシ（Reverse Proxy）<br>
> クライアントとサーバの通信の間に入って、サーバの応答を「代理（proxy）」しつつ通信を中継する機能、あるいはその役割を担うサーバ。<br>
> 具体的な役割としては、｛ロードバランシング・コンテンツキャッシュ、HTTPS通信の終端化、アクセス制御・リクエストの書き換え・gzip圧縮転送・ロギング・バッファリング｝など。<br>
> Webシステムのセキュリティ対策や性能向上、負荷分散、あるいはシステム構成の自由度向上などのためによく利用される。

> - リバースプロキシとロードバランサーの違い
> ロードバランサーが分散負荷（ロードバランシング）を行うだけのものに対して、リバースプロキシは分散負荷を含めたより総合的な処理を行っているという違いがある。

## ■ 使用法

1. nginx をインストールする<br>
    - MacOS の場合
        ```sh
        $ brew install nginx
        ```
    - Ubuntu の場合
        ```sh
        ```

- リバースプロキシへの対応<br>
    リバースプロキシとしての Web サーバーを構築する場合は、`nginx.conf` の HTTP モジュールに以下のような設定を追加すれればよい
    ```conf
    http{
        server {
            listen 80;                          # リバースプロキシとしての nginx サーバーの IP アドレスとポート番号（ポート番号のみの指定も可能）
            server_name localhost;              # リバースプロキシとしての nginx サーバーのドメイン名（www.example.com など）

            # nginx をリバースプロキシとして利用するための設定
            proxy_redirect                          off;
            proxy_set_header    Host                $host;
            proxy_set_header    X-Real-IP           $remote_addr;
            proxy_set_header    X-Forwarded-Host    $host;
            proxy_set_header    X-Forwarded-Server  $host;
            proxy_set_header    X-Forwarded-Proto   $scheme;
            proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;

            # location で URI のパス毎の設定を記述可能（location / => リクエストURIのパスが "/", location /example/ => リクエストURIのパスが "/example"）
            # nginx をリバースプロキシとして利用する場合は、location を利用して、分散負荷先のリクエスト URL を個別に設定する
            location /example1/ {
                proxy_pass    http://${IP_ADRESS1}:${PORT1};       # 分散負荷先１のリクエスト URL
            }

            location /example2/ {
                proxy_pass    http://${IP_ADRESS2}:${PORT2};       # 分散負荷先２のリクエスト URL
            }
        }
    }
    ```

    例えば、以下の図のような構成にする場合は


1. `nginx` コマンドで Nginx の Web サーバーを起動する<br>
    リバースプロキシ用に修正した `nginx.conf` を `-c` オプションで指定した以下のコマンドで Nginx の Web サーバーを起動する。
    ```sh
    $ nginx -c ${NGINX_CONF_FILE_PATH}
    ```

1. Web サーバーにブラウザアクセスする<br>
    プロキシサーバのドメイン名とポート番号でアクセスする。
    ```sh
    $ curl http://localhost:80
    ```

    ブラウザアクセスする場合は、以下のコマンドを実行
    - MacOS の場合
        ```sh
        # 8080 版ポートの場合
        $ open http://localhost:80
        ```

## ■ 参考サイト
- http://tech.respect-pal.jp/reverse_proxy_cooking/
- https://qiita.com/yktk435/items/46f3a0d07145ea767621
- https://qiita.com/riita10069/items/5d36dfeb756e3b6c4978#%E3%83%AA%E3%83%90%E3%83%BC%E3%82%B9%E3%83%97%E3%83%AD%E3%82%AD%E3%82%B7

