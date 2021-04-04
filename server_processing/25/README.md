# 【nginx】リバースプロキシとしての nginx をロードバランサーとして利用する。
xxx

- ToDo
    - リバースプロキシにアクセスしたときに、"Hello Server1!" しか表示されずロードバランシングしていない問題の解消。"Hello Server1!" or "Hello Server2!" が表示されるのが正しい動作


## ■ 手順
ここでの説明は、以下のような構成のシステムを構築する場合の手順を記載する。<br>
<img src="https://user-images.githubusercontent.com/25688193/113479439-1a458380-94ca-11eb-98e0-e2df9f9264cc.png" width="400"><br>


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
            # upstream ディレクティブの中にロードバランシングを行う Web サーバ群のリストを記述
            # ここでは my_servers と命名（名前は任意）
            upstream my_servers {
                server localhost:8080;
                server localhost:8081;
            }

            server {
                listen 80;                          # リバースプロキシとしての nginx サーバーの IP アドレスとポート番号（ポート番号のみの指定も可能）
                server_name localhost;              # リバースプロキシとしての nginx サーバーのドメイン名（www.example.com など）
                root        /Users/sakai/GitHub/MachineLearning_Tips/server_processing/25/nginx/html;
                index       index_proxy.html;
                charset UTF-8;                      # レスポンスヘッダの Content-type

                # nginx をリバースプロキシとして利用するための設定
                proxy_set_header    Host                $host;
                proxy_set_header    X-Real-IP           $remote_addr;
                proxy_set_header    X-Forwarded-Host    $host;
                proxy_set_header    X-Forwarded-Server  $host;
                proxy_set_header    X-Forwarded-Proto   $scheme;
                proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;

                # location ディレクティブで URI のパス毎の設定を記述可能（location / => リクエストURIのパスが "/", location /example/ => リクエストURIのパスが "/example"）
                # リバースプロキシとしての nginx をロードバランサーとして利用する場合は、location を利用して、upstream ディレクティブで設定した名前のリクエスト URL を設定する
                location / {
                    proxy_pass    http://my_servers;       # upstream ディレクティブで指定した名前
                    proxy_redirect default;
                }
            }
        }
        ```

1. Web サーバー用 conf ファイルを作成する。<br>
    分散負荷先の Web サーバーとして nginx を利用する場合は、上記のリバースプロキシ用の conf ファイルとは別に、通常の nginx 設定ファイル作成する。<br>
    - （例）Web サーバー１用 conf ファイル : `server1.conf`
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
                root        /Users/sakai/GitHub/MachineLearning_Tips/server_processing/25/nginx/html;
                index       index_server1.html;
                charset UTF-8;                      # レスポンスヘッダの Content-type
            }
        }
        ```

    - （例）Web サーバー２用 conf ファイル : `server2.conf`
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
                listen 8081;                        # Web サーバーとしての nginx のポート番号
                server_name localhost;              # Web サーバーとしての nginx サーバーのドメイン名（www.example.com など）
                root        /Users/sakai/GitHub/MachineLearning_Tips/server_processing/25/nginx/html;
                index       index_server2.html;
                charset UTF-8;                      # レスポンスヘッダの Content-type
            }
        }
        ```

1. nginx を起動する<br>
    `nginx` コマンドで、リバースプロキシとしての nginx と Web サーバーとしての nginx それぞれを起動する<br>
    ```sh
    $ nginx -c ${PWD}/nginx/proxy.conf       # リバースプロキシとしての nginx を起動
    $ nginx -c ${PWD}/nginx/server1.conf     # Web サーバー１としての nginx を起動
    $ nginx -c ${PWD}/nginx/server2.conf     # Web サーバー２としての nginx を起動
    ```

1. Web サーバーにアクセスする<br>
    プロキシサーバと Web サーバーにアクセスし、動作確認する。
    ```sh
    $ curl http://localhost:80          # リバースプロキシにアクセス
    $ curl http://localhost:8080        # Web サーバー１にアクセス
    $ curl http://localhost:8081        # Web サーバー２にアクセス
    ```

    ブラウザアクセスする場合は、以下のコマンドを実行<br>
    - MacOS の場合
        ```sh
        $ open http://localhost:80      # "Hello Server1" か "Hello Server2" が表示されれば正常に動作している（Hello Proxy! ではないことに注意）
        $ open http://localhost:8080    # "Hello Server1" が表示されれば正常に動作している
        $ open http://localhost:8081    # "Hello Server2" が表示されれば正常に動作している
        ```

## ■ 参考サイト
- http://tech.respect-pal.jp/reverse_proxy_cooking/
