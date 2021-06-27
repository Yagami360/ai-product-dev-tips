# 【MySQL】MySQL に Web-API のログデータを書き込む（FastAPI + uvicorn + gunicorn + MySQL + SQLAlchemy + docker + docker-compose での構成）

<img src="https://user-images.githubusercontent.com/25688193/123530517-2aba7280-d736-11eb-8c10-159f5e488761.png" width="500"><br>

## ■ 方法

1. Web-API のコードを作成する<br>
    SQLAlchemy を使用して MySQL へログデータを書き込む処理も追加した Web-API のコードを作成する<br>
    ここでは、Web フレームワークとして FastAPI を使用している。

    - `mysql_utils/config.py` : SQLAlchemy での各種設定ファイル<br>
        ```python
        # coding=utf-8
        import os

        class MySQLConfig:
            # クラス変数
            username=os.getenv("MYSQL_USER")
            password=os.getenv("MYSQL_PASSWORD")
            db_name=os.getenv("MYSQL_DATABASE")
            host=os.getenv("MYSQL_HOST")
            port=int(os.getenv("MYSQL_PORT", 3306))
            database_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}?charset=utf8"
        ```

        > 後述の `docker-compose.yml` の `environment` タグで定義した各種環境変数を `os.getenv()` で読み込み、その環境変数の値で初期化するようにしている

        > 環境変数 `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` は、MySQL サーバーの docker image `mysql:5.7` 内部でも使用される環境変数。

        > 環境変数 `MYSQL_HOST`, `MYSQL_PORT` は、MySQL サーバーの docker image `mysql:5.7` 内部では使用されない環境変数であるが、`docker-compose.yml` の API サーバーの `environment` タグで独自に定義した環境変数となる


    - `mysql_utils/setting.py` : SQLAlchemy での Engine, Seesion, Base の作成<br>
        SQLAlchemy ではまず初めに、Engine, Seesion, Base を作成する必要があるが、このスクリプトではこれらの初期化処理を行っている
        ```python
        # coding=utf-8
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from sqlalchemy.ext.declarative import declarative_base
        from contextlib import contextmanager

        from mysql_utils.config import MySQLConfig

        # engine 作成
        engine = create_engine(
            MySQLConfig.database_url,
            encoding="utf-8",
            pool_recycle=3600,
            echo=True,                # True : 実行のたびにSQLが出力される
        )

        # Session クラス作成
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # sessionmaker インスタンスを内包した scoped_session インスタンスを生成
        # sessionmaker との違いは、Session() を何回実行しても同一の Session が返されるという点
        global_session = scoped_session(Session)

        # Base クラス（独自に定義するテーブルデータに対応するモデルクラスの基底クラス）を作成
        Base = declarative_base()

        # 予め Base クラスに query プロパティを仕込んでおく
        #Base.query = global_session.query_property()

        def get_session():
            session = Session()
            try:
                yield session
            except:
                session.rollback()
                raise
            finally:
                session.close()

        @contextmanager
        def get_context_session():
            """
            with 構文で使う session
            with get_context_session() as session
                ...
            の形式で使用する
            """
            session = Session()
            try:
                yield session
            except:
                session.rollback()      # session.commit() 失敗時は、MySQL のデータをもとに戻す
                raise
            finally:
                session.close()
        ```

        > テーブルデータクラスの基底クラスである `Base` クラスの継承クラスを MySQL のデータベースに登録した後に、MySQL データベースへのアクセスが可能になるが、この登録処理は、`Base` クラスの継承クラスを定義した後に行わう必要があるので、後述の `mysql_utils/crud.py` の `init()` メソッドで行うようにしている

        > `@contextmanager` と使用して、API コードから with 構文で session を使用できる `get_context_session()` メソッドも追加している

    - `mysql_utils/models.py` : MySQL に書き込むテーブルデータを定義<br>
        ```python
        # coding=utf-8
        from sqlalchemy import Column, Integer, String, Float, DateTime
        from sqlalchemy import Column, DateTime, String
        from sqlalchemy.sql.functions import current_timestamp
        from sqlalchemy.types import JSON

        from mysql_utils.setting import Base

        class LogTable(Base):
            """
            MySQL のデータベースに保存するテーブルデータを定義したモデルクラス
            """
            # クラス変数
            __tablename__ = "log_table"
            log_id = Column( String(255), primary_key=True)     # ログデータの識別 ID
            log = Column( JSON, nullable=False)                 # ログデータ（json）
            datetime = Column( DateTime(timezone=True), server_default=current_timestamp(), nullable=False)     # タイムスタンプ
        ```

    - `mysql_utils/crud.py` : MySQL データベースへの CRUD 処理<br>
        MySQL へのログデータの書き込みや読み込みは、このスクリプト内で定義した各種メソッド群を呼び出すことで行えるように実装している

        ```python
        # coding=utf-8
        from sqlalchemy import Column, Integer, String, Float, DateTime

        from mysql_utils.config import MySQLConfig
        from mysql_utils.setting import engine, Base
        from mysql_utils.models import LogTable


        def init(checkfirst=True):
            """
            MySQL のデータベースにテーブルデータを登録する。
            Base を継承したテーブルデータクラス定義後に、一度実行する必要がる
            """
            # Base を継承したテーブルデータクラス全てが、MySQL のデータベースに登録される
            # create_all() を１度実行済みで、テーブルを再作成する場合は　checkfirst=False を設定
            Base.metadata.create_all(bind=engine, checkfirst=checkfirst)
            return

        def insert(session, id=0, data=None, commit=True):
            """
            MySQL データベースにテーブルデータを INSERT する（書き込む）
            """
            data = LogTable(log_id=id, log=data)
            session.add(data)
            if(commit):
                session.commit()
                session.refresh(data)
            return data

        def select_first(session):
            """
            MySQL データベースに保存されている最初のレコードのテーブルデータを SELECT する（読み込む）
            """
            # テーブルデータの最初のレコードのオブジェクトで返す
            data = session.query(LogTable).first()
            return data

        def select_all(session):
            """
            MySQL データベースに保存されている全レコードのテーブルデータを SELECT する（読み込む）
            """
            # テーブルデータの全レコードのオブジェクトが入った配列で返す
            data = session.query(LogTable).all()
            return data
        ```

        > テーブルデータクラスの基底クラスである `Base` クラスの継承クラス `LogTable` を `Base.metadata.create_all(bind=engine)` メソッドで MySQL のデータベースに登録した後に、初めて MySQL データベースへのアクセスが可能になる。そのため、この登録処理を行う `init()` メソッドを定義している。        
        > この登録処理は、`Base` クラスの継承クラスを定義した後に行う必要があるので、`init()` メソッドは、`LogTable` クラス定義後に一度呼び出される必要がある

    - `mysql_utils/converter.py` : json 形式への変換スクリプト<br>
        SQLAlchemy でのテーブルデータクラス（`Base` クラスの継承クラス）のオブジェクトを Web-API のレスポンスデータとしてそのまま返すとエラーになるので、テーブルデータクラスのオブジェクトをレスポンスデータとして指定可能な json 形式に変数するコードも追加する
        ```python
        # coding=utf-8
        import json
        from sqlalchemy.ext.declarative import DeclarativeMeta

        class AlchemyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj.__class__, DeclarativeMeta):
                    # an SQLAlchemy class
                    fields = {}
                    for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                        data = obj.__getattribute__(field)
                        try:
                            json.dumps(data) # this will fail on non-encodable values, like other classes
                            fields[field] = data
                        except TypeError:
                            fields[field] = None
                    # a json-encodable dict
                    return fields

                return json.JSONEncoder.default(self, obj)

        def convert_table_to_json(data):
            """
            テーブルデータを json 形式に変換する
            """
            json_data = json.dumps(data, cls=AlchemyEncoder)
            return json_data
        ```

    - `api/app.py` : FastAPI でのコード<br>
        Web フレームワークとして FastAPI を使用した Web-API のコード<br>
        上記作成した SQLAlchemy の utils コード群 `mysql_utils/*` を使用して、MySQL のデータベースにログデータの書き込み処理も行う
        ```python
        ```

        > SQLAlchemy でのテーブルデータクラス `LogTable` を MySQL に書き込み or 読み込み可能にするためには、最初に `Base.metadata.create_all(bind=engine)` でこのテーブルデータクラスを MySQL データベースに登録する必要があるが、独自に定義した `crud.init()` メソッドを app.py の先頭部分で呼び出すことで、この初期化処理を行っている

        > FastAPI の `BackgroundTask` モジュールの `add_task()` メソッドを使用して、MySQL へのログデータの書き込み処理をバックグラウンド処理で行うようにしている。バックグラウンド処理を行うことで Web-API の本来の処理のパフォーマンスを失わないようになる。バックグラウンドで行うことで、MySQL へのログデータ書き込みが遅延する可能性はあるが、少し時間をまってログデータを読み込めばよいだけなので大きな問題はない

1. Web-API の Dockerfile を作成する<br>
    ```Dockerfile
    #-----------------------------
    # Docker イメージのベースイメージ
    #-----------------------------
    FROM python:3.8-slim
    #FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

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

    RUN pip3 install --upgrade pip

    #-----------------------------
    # 環境変数
    #-----------------------------
    ENV LC_ALL=C.UTF-8
    ENV export LANG=C.UTF-8
    ENV PYTHONIOENCODING utf-8

    #-----------------------------
    # 追加ライブラリのインストール
    #-----------------------------
    RUN pip3 install fastapi
    RUN pip3 install uvicorn
    RUN pip3 install Gunicorn
    RUN pip3 install requests

    RUN pip3 install PyMySQL
    RUN pip3 install sqlalchemy

    #-----------------------------
    # ソースコードの書き込み
    #-----------------------------
    #COPY *.py /api/
    #COPY utils/*.py /api/utils/
    #COPY log/*.log /api/log/

    #-----------------------------
    # ポート開放
    #-----------------------------
    EXPOSE 5000

    #-----------------------------
    # コンテナ起動後に自動的に実行するコマンド
    #-----------------------------
    # docker-compose で起動定義するのでコメントアウト
    #CMD ["gunicorn","app:app","--bind","0.0.0.0:5000","-w","1","-k","uvicorn.workers.UvicornWorker","--reload"]

    #-----------------------------
    # コンテナ起動後の作業ディレクトリ
    #-----------------------------
    WORKDIR /api
    ```

    > SQLAlchemy を使用するために、`RUN pip3 install PyMySQL` と `RUN pip3 install sqlalchemy` を追加している

1. MySQL 設定ファイル `my.cnf` を作成する<br>
    例えば、以下のような MySQL サーバーの設定ファイル `my.cnf` を作成し、`mysql/my.cnf` 以下に保存する
    ```ini
    [client]
    default-character-set=utf8mb4

    [mysqld]
    character-set-server=utf8mb4
    collation-server=utf8mb4_unicode_ci
    ```

    > この設定ファイル `my.cnf` は、後述の docker-compose の volumes タグで、MySQL docker image の `/etc/my.cnf` にマウントすることで、MySQL サーバーに反映させる.

1. `docker-compose.yml` を作成する<br>
    MySQL サーバーと Web-API サーバーを定義した `docker-compose.yml` を作成する
    ```yml
    version: '2.3'

    services:
    # MySQL サーバー
    mysql-server:
        container_name: mysql-container
        image: mysql:5.7
        ports:
            - "3306:3306"
        tty: true
        volumes:
            - ${PWD}/mysql/my.cnf:/etc/my.cnf                         # 作成した MySQL の設定ファイル `my.cnf` を `mysql:latest` の設定ファイル `/etc/my.cnf` にマウントして差し替える
            - ${PWD}/mysql/db/data:/var/lib/mysql                     # MySQL のデータが保存されているディレクトリ `/var/lib/mysql` をローカルディレクトリにマウント
            - ${PWD}/mysql/db/initdb.d:/docker-entrypoint-initdb.d    # 
        restart: always                                             # 終了ステータスが異常の場合も常に再起動
        stdin_open: true                                            # コンテナの標準入力をオープンしたままにする。`docker run` での `-i` オプションに対応
        environment:                                                # MySQL の docker image `mysql` で使用される環境変数を追加
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
            MYSQL_ROOT_PASSWORD: password                             # [必須] root ユーザーに対しての MySQL ログインパスワード
            MYSQL_USER: user                                          # [オプション] MySQL サーバー起動時に作成するデータベース名
            MYSQL_PASSWORD: password                                  # [オプション] 新規ユーザーに対しての MySQL ログインパスワード            
            MYSQL_DATABASE: "test_db"                                 # [オプション] MySQL サーバー起動時に作成するデータベース名

    # Web-API サーバー
    fast-api-mysql-server:
        container_name: fast-api-mysql-container
        image: fast-api-mysql-image
        build:
            context: "api/"
            dockerfile: Dockerfile_dev
        volumes:
            - ${PWD}/api:/api
            - ${PWD}/mysql_utils:/mysql_utils
        ports:
            - "5000:5000"
        tty: true
        environment:                                                # config.py のための環境変数を追加
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
            MYSQL_ROOT_PASSWORD: password                             
            MYSQL_USER: user                                          
            MYSQL_PASSWORD: password                                           
            MYSQL_DATABASE: "test_db"  
            MYSQL_HOST: "mysql-server"                               # コンテナ間で接続する場合は、MySQL サーバーのホスト名は、localhost ではなく `services` タグで定義したサービス名で指定                              
            MYSQL_PORT: "3306"
        depends_on:
            - mysql-server
        command: bash -c "gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"
    ```

    MySQL サーバーに関してのポイントは、以下の通り<br>
    > - `volumes` タグで、作成した設定ファイル `mysql/my.cnf` を `/etc/my.cnf` にマウント<br>
    >    MySQL docker image `mysql` では、`/etc/my.cnf` にある設定ファイルで MySQL サーバーが起動されるので、作成した設定ファイル `mysql/my.cnf` をこのディレクトリにマウントし、設定ファイルが反映させるようにする<br>

    > - MySQL の環境変数を追加<br>
    >    `environment` タグに、MySQL の docker image `mysql` で使用される環境変数 `MYSQL_ROOT_PASSWORD`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` を設定することで、その設定値を反映した MySQL サーバーが実行される。<br>
    >    ここで、MySQL サーバーのホスト名とポート番号を設定する環境変数は、用意されていないことに注意。ホスト名とポート番号は、MySQL 設定ファイル `etc/my.cnf` で設定できるが、特に設定しなかった場合は、デフォルト値の "localhost" と `3306` になる<br>
    
    > - コンテナ起動時の `command` は使用しない<br>
    >   MySQL の docker image `mysql` では、docker image 起動時に、エンドポイントのスクリプト `/entrypoint.sh` が実行され、`mysqld` コマンドが自動的に実行されので、コンテナ起動時に `command` タグで MySQL サーバーを起動する処理を行う必要はない

    Web-API サーバーに関してのポイントは、以下の通り<br>
    > - MySQL の環境変数とホスト名とポート番号の環境変数を追加<br>
    >    `environment` タグに、MySQL の docker image `mysql` で使用される環境変数 `MYSQL_ROOT_PASSWORD`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` と同じ名前の環境変数を設定している。また MySQL サーバーに接続するためのホスト名とポート番号の環境変数 `MYSQL_HOST`, `MYSQL_PORT` も追加している。
    > これらの環境変数は、`mysql_utils/config.py` にて、SQLAlchemy の設定値として読み込まれて使用される

    > - コンテナ間通信時のホスト名<br>
    >   MySQL サーバーに接続するためのホスト名の環境変数 `MYSQL_HOST` は、`localhost` ではなく、docker-compose での MySQL サーバーのサービス名 `mysql-server` にしている。これは、docker-compose 内でのコンテナ間通信では、`localhost` が認識できないためである。

1. `docker-compose` コマンドで、MySQL サーバーを起動する<br>
    ```sh
    $ docker-compose -f docker-compose.yml stop
    $ docker-compose -f docker-compose.yml up -d
    $ sleep 5
    ```

1. Web-API に対してリクエスト処理を行う<br>
    Web-API に対してリクエスト処理を行う<br>
    このとき Web-API は、自身のログデータを MySQL データベースに書き込む動作になっている。
    ```sh
    ```

1. Web-API に対して、ログデータ取得のリクエスト処理を行う<br>
    ```sh
    # ログデータを取得
    echo "[GET method] MySQL データベースの全ログデータを取得\n"
    curl http://${HOST}:${PORT}/log_all
    echo "\n"

    echo "[GET method] MySQL データベースの最初のログデータを取得\n"
    curl http://${HOST}:${PORT}/log_first
    echo "\n"
    ```

    正常に動作している場合は、MySQL に書き込まれたログデータがレスポンスされる
    ```sh
    ```
