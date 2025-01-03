# 【nginx】nginx をリバースプロキシとして利用する
Nginx は、単一の Web サーバーとしての機能させるだけでなく、クライアントとサーバの通信の間に入って分散負荷等を行うリバースプロキシとして機能させることもできる。

> - リバースプロキシ（Reverse Proxy）<br>
> クライアントとサーバの通信の間に入って、サーバの応答を「代理（proxy）」しつつ通信を中継する機能、あるいはその役割を担うサーバ。<br>
> 具体的な役割としては、｛ロードバランシング・コンテンツキャッシュ、HTTPS通信の終端化、アクセス制御・リクエストの書き換え・gzip圧縮転送・ロギング・バッファリング｝など。<br>
> Webシステムのセキュリティ対策や性能向上、負荷分散、あるいはシステム構成の自由度向上などのためによく利用される。

> - リバースプロキシとロードバランサーの違い
> ロードバランサーが分散負荷（ロードバランシング）を行うだけのものに対して、リバースプロキシは分散負荷を含めたより総合的な処理を行っているという違いがある。

## ■ 使用法
ここでの説明は、以下のような構成のシステムを構築する場合の手順を記載する。<br>

<img src="https://user-images.githubusercontent.com/25688193/113480517-8a0a3d00-94cf-11eb-8395-11d15a72a27f.png" width="500"><br>

1. リバースプロキシ用 conf ファイルを作成する。<br>
    リバースプロキシとしての nginx を構築する場合は、以下のような conf ファイルを作成すればよい。HTTP モジュールに追加されている構文に注目<br>

    - 例 : リバースプロキシ用 conf ファイル : `proxy.conf`
        ```conf
        #----------------
        # Core モジュール。
        # プロセスの管理・設定ファイル制御・セキュリティ・ロギングなどの設定を行う。
        #----------------
        worker_processes  auto;         # 実行プロセス数
        include servers/*;              # nginx.conf 以外の読み込みファイルの読み込みパス

        #----------------
        # Events モジュール。
        # イベント処理(パフォーマンス・チューニングなどの設定を行う
        #----------------
        events {
            worker_connections  1024;   # コネクション数（同時接続数？）の制限
        }

        #----------------
        # HTTP モジュール。
        # Web サーバーに関しての設定を行う
        #----------------
        http{
            server {
                listen 80;                          # リバースプロキシとしての nginx サーバーの IP アドレスとポート番号（ポート番号のみの指定も可能）
                server_name localhost;              # リバースプロキシとしての nginx サーバーのドメイン名（www.example.com など）
                root        /Users/sakai/GitHub/MachineLearning_Tips/server_processing/24/nginx/html;
                index       index_proxy.html;
                charset UTF-8;                      # レスポンスヘッダの Content-type

                # nginx をリバースプロキシとして利用するための設定
                #proxy_redirect                          off;
                proxy_set_header    Host                $host;
                proxy_set_header    X-Real-IP           $remote_addr;
                proxy_set_header    X-Forwarded-Host    $host;
                proxy_set_header    X-Forwarded-Server  $host;
                proxy_set_header    X-Forwarded-Proto   $scheme;
                proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;

                # location で URI のパス毎の設定を記述可能（location / => リクエストURIのパスが "/", location /example/ => リクエストURIのパスが "/example"）
                # nginx をリバースプロキシとして利用する場合は、location を利用して、分散負荷先のリクエスト URL を個別に設定する
                location / {
                    proxy_pass    http://localhost:8080;       # 分散負荷先サーバー１のリクエスト URL
                }
            }
        }
        ```

1. Web サーバー用 conf ファイルを作成する。<br>
    分散負荷先の Web サーバーとして nginx を利用する場合は、上記のリバースプロキシ用の conf ファイルとは別に、通常の nginx 設定ファイル作成する。<br>
    - （例）Web サーバー用 conf ファイル : `server.conf`
        ```conf
        #----------------
        # Core モジュール。
        # プロセスの管理・設定ファイル制御・セキュリティ・ロギングなどの設定を行う。
        #----------------
        worker_processes  auto;         # 実行プロセス数
        include servers/*;              # nginx.conf 以外の読み込みファイルの読み込みパス

        #----------------
        # Events モジュール。
        # イベント処理(パフォーマンス・チューニングなどの設定を行う
        #----------------
        events {
            worker_connections  1024;   # コネクション数（同時接続数？）の制限
        }

        #----------------
        # HTTP モジュール。
        # Web サーバーに関しての設定を行う
        #----------------
        http{
            # サーバの構築
            server {
                listen 8080;                        # Web サーバーとしての nginx のポート番号
                server_name localhost;              # Web サーバーとしての nginx サーバーのドメイン名（www.example.com など）
                root        /Users/sakai/GitHub/MachineLearning_Tips/server_processing/24/nginx/html;
                index       index_server.html;
                charset UTF-8;                      # レスポンスヘッダの Content-type
            }
        }
        ```

1. nginx を起動する<br>
    `nginx` コマンドで、リバースプロキシとしての nginx と Web サーバーとしての nginx それぞれを起動する<br>
    ```sh
    $ nginx -c ${PWD}/nginx/proxy.conf       # リバースプロキシとしての nginx を起動
    $ nginx -c ${PWD}/nginx/server1.conf     # Web サーバーとしての nginx を起動
    ```

1. Web サーバーにアクセスする<br>
    プロキシサーバと Web サーバーにアクセスし、動作確認する。
    ```sh
    $ curl http://localhost:80          # リバースプロキシにアクセス
    $ curl http://localhost:8080        # Web サーバーにアクセス
    ```

    ブラウザアクセスする場合は、以下のコマンドを実行<br>
    - MacOS の場合
        ```sh
        $ open http://localhost:80      # "Hello Server!" が表示されれば正常に動作している（Hello Proxy! ではないことに注意）
        $ open http://localhost:8080    # "Hello Server!" が表示されれば正常に動作している
        ```

## ■ 参考サイト
- http://tech.respect-pal.jp/reverse_proxy_cooking/
- https://qiita.com/yktk435/items/46f3a0d07145ea767621
- https://qiita.com/riita10069/items/5d36dfeb756e3b6c4978#%E3%83%AA%E3%83%90%E3%83%BC%E3%82%B9%E3%83%97%E3%83%AD%E3%82%AD%E3%82%B7

