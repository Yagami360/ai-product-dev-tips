# 【uWSGI】docker + nginx + uWSGI + Flask を用いた Web-API の構築
Flask を用いれば、nginx や uWSGI がなくとも、Flaskの run メソッドを使用して、簡単に Web-API を構築することができる。<br>
しかしながら、この Flaskの run メソッドは、テスト用環境での使用のみが推奨されており、本番環境での使用は推奨されていない。（例えば、Flask でのメモリ使用量が爆発してしまうなどの不具合が発生するケースがある）

そのため、Flask を用いて本番環境の Web-API を構築する際には、下図のように「client ↔ nginx ↔ uWSGI ↔ Flask」の構成でシステムを構築するのが通例になっている。<br>

<img src="https://user-images.githubusercontent.com/25688193/113583847-1b5ee800-9665-11eb-9a73-3b47c60942ce.png" width="400"><br>

## ■ 手順
ここでは、以下のような構成の Web-API を構築する際の手順を示す。<br>
<img src="https://user-images.githubusercontent.com/25688193/113584380-cb345580-9665-11eb-8647-b77ceee06663.png" width="400"><br>

1. uWSGI + Flask-API サーバーの構築<br>
    1. Flask-API のコード `app.py` を作成する。<br>
        ここでは、簡単な例として `api/app.py` に "Hello Flask-API Server!" を表示するような Flask-API を作成する。

        > `api/app.py` の実行は、後述の docker-compose 内にて、`uwsgi` コマンドを用いて `app.py` を実行する形式になるが、`uwsgi` コマンドを用いて `app.py` を実行する場合はｍ`app.py` で `import argparse` して定義しているコマンドライン引数は使えないことに注意。<br>
        > `app.py` でコマンドライン引数を使いたい場合は、Python の `sys.argv` を使用し、uWSGI の設定ファイル（`*.ini`形式）内で、`pyargv "args1 args2"` という形式のオプションを追加する方法がある。<br>

    1. uWSGI 設定ファイル `*.ini` を作成する。<br>
        Flask-API サーバー１とFlask-API サーバー２用の uWSGI 設定ファイル `*.ini` を作成する。<br>
        - Flask-API サーバー１用 uWSGI 設定ファイルの例 : `uwsgi_server1.ini`
            ```ini
            [uwsgi]
            wsgi-file=app.py
            callable=app
            http=0.0.0.0:5000
            #http-socket = :5000
            processes = 1
            threads = 1
            ```
        - Flask-API サーバー１用 uWSGI 設定ファイルの例 : `uwsgi_server2.ini`
            ```ini
            [uwsgi]
            wsgi-file=app.py
            callable=app
            http=0.0.0.0:5001
            #http-socket = :5000
            processes = 1
            threads = 1
            ```

    1. uWSGI + Flask-API の `Dockerfle` を作成する<br>
        flask と uwsgi をインストールした dockerfile を作成する。<br>
        ```Dockerfile
        #-----------------------------
        # Docker イメージのベースイメージ
        #-----------------------------
        FROM ubuntu:16.04

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
        # 追加ライブラリのインストール
        #-----------------------------
        # miniconda のインストール
        RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
        RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
        RUN rm Miniconda3-latest-Linux-x86_64.sh
        ENV PATH=/miniconda/bin:${PATH}
        RUN conda update -y conda
            
        # conda 上で Python 3.6 環境を構築
        ENV CONDA_DEFAULT_ENV=py36
        RUN conda create -y --name ${CONDA_DEFAULT_ENV} python=3.6.9 && conda clean -ya
        ENV CONDA_PREFIX=/miniconda/envs/${CONDA_DEFAULT_ENV}
        ENV PATH=${CONDA_PREFIX}/bin:${PATH}
        RUN conda install conda-build=3.18.9=py36_3 && conda clean -ya

        # Other (for server)
        RUN conda install -c anaconda flask && conda clean -ya
        RUN conda install -c anaconda flask-cors && conda clean -ya
        RUN conda install -c anaconda requests && conda clean -ya
        RUN conda install -c anaconda requests && conda clean -ya
        RUN conda install -c conda-forge uwsgi && conda clean -ya

        #-----------------------------
        # ソースコードの書き込み
        #-----------------------------
        #WORKDIR /api
        #COPY *.py /api/

        #-----------------------------
        # ポート開放
        #-----------------------------
        EXPOSE 5000
        EXPOSE 5001

        #-----------------------------
        # コンテナ起動後に自動的に実行するコマンド
        #-----------------------------
        # docker-compose で起動定義するのでコメントアウト
        #CMD ["uwsgi","--ini","uwsgi.ini"]

        #-----------------------------
        # コンテナ起動後の作業ディレクトリ
        #-----------------------------
        WORKDIR /api        
        ```

1. リバースプロキシとしての nginx 設定<br>
    1. nginx の設定 conf ファイルを作成する<br>
        nginx をリバースプロキシ（ロードバランサーあり）として動作させるために、「[【nginx】docker + nginx + Flask を用いた Web-API の構築](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/26)」記載の方法と同様の方法で、nginx の設定 conf ファイルを作成する。<br>

        uWSGI を使用する場合は、更に HTTP モジュールの location ディレクティブ内で `uwsgi_params` ファイルを include する設定を追加する必要がある。<br>
        この設定により、server ディレクティブで定義した nginx サーバーアドレス（ここでは localhost:8080）アクセス時に、uWSGI に接続されるようになる。<br>

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
                    include         /etc/nginx/uwsgi_params; # nginx インストール時に作成された uWSGI 用設定ファイルのデフォルトパスを指定
                    proxy_pass      http://my_servers;       # upstream ディレクティブで指定した名前
                    proxy_redirect  default;
                }
            }
        }
        ```

        > `uwsgi_params` ファイルは nginx インストール時に自動的に作成されるが、ファイルの場所は OS 環境などにより異なることに注意。<br>
        > Ubuntu 環境の場合は、`/etc/nginx/uwsgi_params` に存在する。

        > 【補足】<br>
        > `uwsgi_params` の中身は、以下のようなファイルになっている。
        > ```
        > uwsgi_param  QUERY_STRING       $query_string;
        > uwsgi_param  REQUEST_METHOD     $request_method;
        > uwsgi_param  CONTENT_TYPE       $content_type;
        > uwsgi_param  CONTENT_LENGTH     $content_length;
        > uwsgi_param  REQUEST_URI        $request_uri;
        > uwsgi_param  PATH_INFO          $document_uri;
        > uwsgi_param  DOCUMENT_ROOT      $document_root;
        > uwsgi_param  SERVER_PROTOCOL    $server_protocol;
        > uwsgi_param  REQUEST_SCHEME     $scheme;
        > uwsgi_param  HTTPS              $https if_not_empty;
        > uwsgi_param  REMOTE_ADDR        $remote_addr;
        > uwsgi_param  REMOTE_PORT        $remote_port;
        > uwsgi_param  SERVER_PORT        $server_port;
        > uwsgi_param  SERVER_NAME        $server_name;
        > ```

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
        # docker-compose で起動定義するのでコメントアウト
        #CMD ["nginx","-c","/proxy/nginx/proxy.conf", "-g", "daemon off;"]

        #-----------------------------
        # コンテナ起動後の作業ディレクトリ
        #-----------------------------
        WORKDIR /proxy
        ```

1. 「リバースプロキシ（nginx）＋ WSGIサーバー（uWSGI）+ Web API サーバー（Flask）」の `docker-compose.yml` を作成する。<br>
    `python3 app.py` で Flask-API サーバーを直接起動するのではなくて、`uwsgi` コマンドを使って uWSGI 経由で Flask-API サーバーを起動している点に注意

    ```yml
    version: '2.3'

    services:
        uwsgi_flask_api_server1:
            container_name: uwsgi-flask-api-container1
            image: uwsgi-flask-api-image
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
            #command: bash -c "python3 app.py"
            command: bash -c "uwsgi --ini uwsgi_server1.ini"

        uwsgi_flask_api_server2:
            container_name: uwsgi-flask-api-container2
            image: uwsgi-flask-api-image
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
            #command: bash -c "python3 app.py"
            command: bash -c "uwsgi --ini uwsgi_server2.ini"

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
                - uwsgi_flask_api_server1
                - uwsgi_flask_api_server2
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
    $ curl http://localhost:5000        # uWSGI 経由で Flask-API サーバー１にアクセス
    $ curl http://localhost:5001        # uWSGI 経由で Flask-API サーバー２にアクセス
    ```

    ブラウザアクセスする場合は、以下のコマンドを実行<br>
    - MacOS の場合
        ```sh
        $ open http://localhost:8080    # nginx リバースプロキシにアクセス
        $ open http://localhost:5000    # uWSGI 経由で Flask-API サーバー１にアクセス
        $ open http://localhost:5001    # uWSGI 経由で Flask-API サーバー２にアクセス
        ```



## ■ 参考サイト
- https://serip39.hatenablog.com/entry/2020/07/06/070000
- https://qiita.com/souchan-t/items/8fb5a5df85882c295d96
