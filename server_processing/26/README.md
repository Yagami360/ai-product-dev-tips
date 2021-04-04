# 【nginx】docker + nginx + Flask を用いた Web-API の構築

## ■ 手順
ここでの説明は、以下のような構成のシステムを構築する場合の手順を記載する。<br>
<img src="https://user-images.githubusercontent.com/25688193/113513147-19345500-95a3-11eb-9542-7bf19ba193c1.png" width="500"><br>

1. Flask-API サーバーの構築<br>
    1. Flask-API のコード `app.py` を作成する。<br>
        ここでは、簡単な例として `api/app.py` に "Hello Flask-API Server! (host=${ホスト名}, port=${ポート番号})" を表示するような Flask-API を作成する
    1. Flask-API の `Dockerfle` を作成する<br>

1. リバースプロキシとしての nginx 設定<br>
    1. nginx の設定 conf ファイルを作成する<br>
        nginx をリバースプロキシ（ロードバランサーあり）として動作させるために、「[【nginx】リバースプロキシとしての nginx をロードバランサーとして利用する。](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/25)」記載の方法で、nginx の設定 conf ファイルを作成する<br>
        この際に、upstream ディレクティブ内では localhost は使えないことに注意が必要<br>
        ```conf
        #----------------
        # Core モジュール。
        # プロセスの管理・設定ファイル制御・セキュリティ・ロギングなどの設定を行う。
        #----------------
        worker_processes  auto;         # 実行プロセス数

        # docker ではコマンドをフォアグラウンドで動かさないとコンテナが停止するが、
        # nginx はデフォルトはバックグラウンド（デーモン）として動くので、フォアグラウンドで nginx プロセスが動くように設定する
        daemon off;

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
                #server localhost:5000;     # upstream ディレクティブ内では localhost は使えないことに注意
                #server localhost:5001;
                server 172.26.0.1:5000;
                server 172.26.0.1:5001;
            }

            # サーバの構築
            server {
                listen 8080;                        # リバースプロキシとしての nginx サーバーの IP アドレスとポート番号（ポート番号のみの指定も可能）
                server_name localhost;              # リバースプロキシとしての nginx サーバーのドメイン名（www.example.com など）
                root        /proxy/nginx/html;
                index       index_proxy.html;
                charset     UTF-8;                  # レスポンスヘッダの Content-type

                # nginx をリバースプロキシとして利用するための設定
                # リバースプロキシに送られるリクエストヘッダの値を再設定している
                proxy_set_header    Host                $host;
                proxy_set_header    X-Real-IP           $remote_addr;
                proxy_set_header    X-Forwarded-Host    $host;
                proxy_set_header    X-Forwarded-Server  $host;
                proxy_set_header    X-Forwarded-Proto   $scheme;
                proxy_set_header    X-Forwarded-For     $proxy_add_x_forwarded_for;

                # location ディレクティブで URI のパス毎の設定を記述可能（location / => リクエストURIのパスが "/", location /example/ => リクエストURIのパスが "/example"）
                # リバースプロキシとしての nginx をロードバランサーとして利用する場合は、location を利用して、upstream ディレクティブで設定した名前のリクエスト URL を設定する
                location / {
                    proxy_pass      http://my_servers;       # upstream ディレクティブで指定した名前
                    proxy_redirect  default;
                }
            }
        }
        ```
    1. nginx の `Dockerfle` を作成する
        ```Dockerfile
        #-----------------------------
        # Docker イメージのベースイメージ
        #-----------------------------
        FROM nginx:latest

        #-----------------------------
        # 基本ライブラリのインストール
        #-----------------------------
        # インストール時のキー入力待ちをなくす環境変数
        ENV DEBIAN_FRONTEND noninteractive

        RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
            sudo \
            git \
            curl \
            wget \
            bzip2 \
            ca-certificates \
            libx11-6 \
            python3-pip \
            procps \
            # imageのサイズを小さくするためにキャッシュ削除
            && apt-get clean \
            && rm -rf /var/lib/apt/lists/*

        #-----------------------------
        # 環境変数
        #-----------------------------
        ENV LC_ALL=C.UTF-8
        ENV export LANG=C.UTF-8
        ENV PYTHONIOENCODING utf-8

        #-----------------------------
        # ポート開放
        #-----------------------------
        EXPOSE 8080

        #-----------------------------
        # コンテナ起動後に自動的に実行するコマンド
        #-----------------------------
        #CMD ["nginx","-c","/proxy/nginx/proxy.conf", "-g", "daemon off;"]

        #-----------------------------
        # コンテナ起動後の作業ディレクトリ
        #-----------------------------
        WORKDIR /proxy
        ```

1. 「リバースプロキシ（nginx）＋ Web API サーバー（Flask）」の `docker-compose.yml` を作成する。
    ```yml
    version: '2.3'

    services:
        flask_api_server1:
            container_name: flask-api-container
            image: flask-api-image
            build:
                context: "api/"
                dockerfile: Dockerfile
            volumes:
                - ${PWD}/api:/api
            ports:
                - "5000:5000"
            tty: true
            environment:
                TZ: "Asia/Tokyo"
                LC_ALL: C.UTF-8
                LANG: C.UTF-8
            command: bash -c "python3 app.py --host 0.0.0.0 --port 5000 --debug"

        flask_api_server2:
            container_name: flask-api-container2
            image: flask-api-image
            build:
                context: "api/"
                dockerfile: Dockerfile
            volumes:
                - ${PWD}/api:/api
            ports:
                - "5001:5001"
            tty: true
            environment:
                TZ: "Asia/Tokyo"
                LC_ALL: C.UTF-8
                LANG: C.UTF-8
            command: bash -c "python3 app.py --host 0.0.0.0 --port 5001 --debug"

        nginx_proxy_server:
            container_name: nginx-proxy-container
            image: nginx-proxy-image
            build:
                context: "proxy/"
                dockerfile: Dockerfile
            volumes:
                - ${PWD}/proxy:/proxy
            ports:
                - "8080:8080"
            links:
                - flask_api_server1
                - flask_api_server2
            tty: true
            environment:
                TZ: "Asia/Tokyo"
                LC_ALL: C.UTF-8
                LANG: C.UTF-8
            command: bash -c "sudo nginx -c /proxy/nginx/proxy.conf"
    ```

1. 「リバースプロキシ（nginx）＋ Web API サーバー（Flask）」を docker-compose で起動する。<br>
    ```sh
    docker-compose -f docker-compose.yml stop
    docker-compose -f docker-compose.yml up -d
    ```

1. 起動した「リバースプロキシ（nginx）＋ Web API サーバー（Flask）」にリクエスト処理を送信し、動作確認する<br>
    ```sh
    $ curl http://localhost:8080        # nginx リバースプロキシにアクセス
    $ curl http://localhost:5000        # Flask-API サーバー１にアクセス
    $ curl http://localhost:5001        # Flask-API サーバー２にアクセス
    ```

    ブラウザアクセスする場合は、以下のコマンドを実行<br>
    - MacOS の場合
        ```sh
        $ open http://localhost:8080    # nginx リバースプロキシにアクセス
        $ open http://localhost:5000    # Flask-API サーバー１にアクセス
        $ open http://localhost:5001    # Flask-API サーバー２にアクセス
        ```

    以下のような動作になってれば、正しく動作している。<br>
	- クライアントから http://localhost:8080 へアクセス時 :<br>
        Hello Flask-API Server! (host=0.0.0.0, port=5000) か Hello Flask-API Server! (host=0.0.0.0, port=5001) が表示
	（Hello Proxy! ではないことに注意）
	- クライアントから http://localhost:5000 へアクセス時 :<br>
        Hello Flask-API Server! (host=0.0.0.0, port=5000) が表示
	- クライアントから http://localhost:5001 へアクセス時 :<br>
    	Hello Flask-API Server! (host=0.0.0.0, port=5001) が表示

### 【補足】 nginx を docker で動かす場合の注意点<br>
docker-compose などで docker コンテナをバックグラウンド実行した場合、コンテナ内でプロセスをフォアグラウンドで動かさないとコンテナが自動的に停止してしまうが、nginx はデフォルトではバックグラウンド実行（デーモン）で動作するために、このままではコンテナ起動後すぐにコンテナが停止してしまう動作となる。<br>
そのため、nginx を docker コマンドで実行するには、以下の２通りの方法で nginx プロセスをフォアグラウンドで動作させるようにする必要があることに注意。

1. nginx 起動コマンドに `-g` オプションを追加する場合
    ```sh
    nginx -g "daemon off;"
    ```

1. conf ファイルに `daemon off;` を追加する場合<br>
    Core モジュールに `daemon off;` を追加することでも
    ```
    #----------------
    # Core モジュール。
    # プロセスの管理・設定ファイル制御・セキュリティ・ロギングなどの設定を行う。
    #----------------
    worker_processes  auto;         # 実行プロセス数

    # docker ではコマンドをフォアグラウンドで動かさないとコンテナが停止するが、
    # nginx はデフォルトはバックグラウンド（デーモン）として動くので、フォアグラウンドで nginx プロセスが動くように設定する
    daemon off;
    ...
    ```

<!--
## 【補足】 `nginx:latest` イメージでの nginx 設定ファイルの構成

- `/etc/nginx/proxy.conf`
    ```conf
    user  nginx;
    worker_processes  1;

    error_log  /var/log/nginx/error.log warn;
    pid        /var/run/nginx.pid;


    events {
        worker_connections  1024;
    }


    http {
        include       /etc/nginx/mime.types;
        default_type  application/octet-stream;

        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';

        access_log  /var/log/nginx/access.log  main;

        sendfile        on;
        #tcp_nopush     on;

        keepalive_timeout  65;

        #gzip  on;

        include /etc/nginx/conf.d/*.conf;
    }
    ```

- `/etc/nginx/conf.d/*.conf`
    ```conf
    ```
-->

## ■ 参考サイト
- http://tech.respect-pal.jp/reverse_proxy_cooking/
- https://heartbeats.jp/hbblog/2014/07/3-tips-for-nginx-on-docker.html
- https://qiita.com/yokomotod/items/46229f0fafd95eb7d867
- https://qiita.com/souchan-t/items/8fb5a5df85882c295d96