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
        Web フレームワークとして FastAPI を使用した Web-API のコード。ここでは、API の簡単な例として Piilow での画像の２値化を行っている<br>
        上記作成した SQLAlchemy の utils コード群 `mysql_utils/*` を使用して、MySQL のデータベースにログデータの書き込み処理も行うようにしている

        ```python
        # coding=utf-8
        import os
        import sys
        import argparse
        import time
        from datetime import datetime
        import logging
        import uuid
        from typing import Any, Dict

        from fastapi import FastAPI
        from fastapi import BackgroundTasks, HTTPException
        from pydantic import BaseModel

        # 自作モジュール
        from utils.logger import log_base_decorator, log_json_base_decorator
        from utils.img_utils import conv_base64_to_pillow, conv_pillow_to_base64
        from config import APIConfig

        sys.path.append(os.path.join(os.getcwd(), '../'))
        from mysql_utils.setting import global_session, get_context_session
        from mysql_utils import crud
        from mysql_utils import converter

        #--------------------------
        # logger
        #--------------------------
        if not os.path.isdir("log"):
            os.mkdir("log")
        if( os.path.exists(os.path.join("log", __name__ + '.log')) ):
            os.remove(os.path.join("log", __name__ + '.log'))

        logger = logging.getLogger(__name__)
        logger.setLevel(10)
        logger_fh = logging.FileHandler(os.path.join("log", __name__ + '.log'))
        logger.addHandler(logger_fh)
        logger.info("{} {} {} start api server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", __name__))

        #--------------------------
        # FastAPI
        #--------------------------
        app = FastAPI()

        class ImageData(BaseModel):
            """
            画像データのリクエストボディ
            """
            image: Any

        #--------------------------
        # MySQL (SQLAlchemy)
        #--------------------------
        crud.init()

        #======================================
        # GET method
        #======================================
        @app.get("/")
        def root():
            return 'Hello Flask-API Server!\n'

        @log_base_decorator(logger=logger)
        def _health():
            return {"health": "ok"}

        @app.get("/health")
        def health():
            return _health()

        @log_base_decorator(logger=logger)
        def _metadata():
            return {
                "APIConfig" : {
                    "threshold": APIConfig.threshold,
                },
            }

        @app.get("/metadata")
        def metadata():
            return _metadata()

        @app.get("/log_all")
        def get_log_all():
            with get_context_session() as session:
                data = crud.select_all(session)
            return converter.convert_table_to_json(data)

        @app.get("/log_first")
        def get_log_first():
            with get_context_session() as session:
                data = crud.select_first(session)
            return converter.convert_table_to_json(data)

        #======================================
        # POST method
        #======================================
        @log_base_decorator(logger=logger)
        def _predict(
            job_id: str,
            img_data: ImageData,
        ):
            # base64 -> Pillow への変換
            img_pillow = conv_base64_to_pillow(img_data.image)

            # ２値化
            img_gray_pillow = img_pillow.convert("L")
            img_gray_pillow.point(lambda x: 0 if x < APIConfig.threshold else x)

            # Pillow -> base64 への変換
            img_base64 = conv_pillow_to_base64(img_gray_pillow)

            return {
                "job_id": job_id,
                "status": "ok",
                "img_base64" : img_base64,
            }

        @app.post("/predict/")
        def predict(
            img_data: ImageData,                # リクエストボディ 
            background_tasks: BackgroundTasks,  # BackgroundTasks
        ):
            start_time = time.time()
            job_id = str(uuid.uuid4())[:6]
            predict_data = _predict(job_id=job_id, img_data=img_data)
            elapsed_time = 1000 * (time.time() - start_time)

            # バックグラウンドで MySQL にログデータを追加
            background_tasks.add_task(
                insert_mysql,                                               # バックグラウンド処理を行うメソッド名
                time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # メソッドの引数
                func_name = sys._getframe().f_code.co_name,                 # ↑
                elapsed_time = elapsed_time,                                # ↑
                job_id = job_id,                                            # ↑
            )

            return predict_data


        def insert_mysql(time_stamp, func_name, elapsed_time, job_id):
            """
            MySQL にログデータ追加
            """
            with get_context_session() as session:
                log = {
                    "time_stamp": time_stamp, 
                    "func_name": func_name,
                    "elapsed_time": elapsed_time,                       
                    "job_id" : job_id,
                }
                crud.insert(session=session, id=job_id, data=log)

            return
        ```

        > ここでは、API 処理の簡単な例として、Pillow での画像の２値化を行っている

        > SQLAlchemy でのテーブルデータクラス `LogTable` を MySQL に書き込み or 読み込み可能にするためには、最初に `Base.metadata.create_all(bind=engine)` でこのテーブルデータクラスを MySQL データベースに登録する必要があるが、独自に定義した `crud.init()` メソッドを app.py の先頭部分で呼び出すことで、この初期化処理を行っている

        > FastAPI の `BackgroundTask` モジュールの `add_task()` メソッドを使用して、MySQL へのログデータの書き込み処理 `insert_mysql()` をバックグラウンド処理で行うようにしている。バックグラウンド処理を行うことで Web-API の本来の処理のパフォーマンスを失わないようになる。バックグラウンドで行うことで、MySQL へのログデータ書き込みが遅延する可能性はあるが、少し時間をまってログデータを読み込めばよいだけなので大きな問題はない

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

    RUN pip3 install Pillow

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

1. リクエスト処理の Python スクリプトを作成する<br>
    上記作成した Web-API にリクエストするためのスクリプトを作成する

    - `request.py`<br>
        ```python
        import os
        import sys
        import argparse
        import json
        from PIL import Image
        from tqdm import tqdm 
        import requests
        import time

        # 自作モジュール
        from api.utils.img_utils import conv_base64_to_pillow, conv_pillow_to_base64

        # グローバル変数
        IMG_EXTENSIONS = (
            '.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif',
            '.JPG', '.JPEG', '.PNG', '.PPM', '.BMP', '.PGM', '.TIF',
        )

        if __name__ == "__main__":
            parser = argparse.ArgumentParser()
            parser.add_argument('--host', type=str, default="localhost", help="API サーバーのホスト名（コンテナ名 or コンテナ ID）")
            parser.add_argument('--port', type=str, default="5000", help="API サーバーのポート番号")
            parser.add_argument('--in_images_dir', type=str, default="in_images", help="入力画像のディレクトリ")
            parser.add_argument('--out_images_dir', type=str, default="out_images", help="出力ディレクトリ")
            parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
            args = parser.parse_args()
            if( args.debug ):
                for key, value in vars(args).items():
                    print('%s: %s' % (str(key), str(value)))
            
            if not os.path.isdir(args.out_images_dir):
                os.mkdir(args.out_images_dir)

            #----------------------------------
            # ヘルスチェック
            #----------------------------------
            health = requests.get( "http://" + args.host + ":" + args.port + "/health" ).json()
            print( "health : ", health )

            #----------------------------------
            # metadata 取得
            #----------------------------------
            metadata = requests.get( "http://" + args.host + ":" + args.port + "/metadata" ).json()
            print( "metadata : ", metadata )

            #----------------------------------
            # predict
            #----------------------------------
            image_names = sorted( [f for f in os.listdir(args.in_images_dir) if f.endswith(IMG_EXTENSIONS)] )
            job_ids = []
            for img_name in tqdm(image_names):
                # リクエスト送信データの設定
                img_pillow = Image.open( os.path.join(args.in_images_dir, img_name) )
                img_base64 = conv_pillow_to_base64(img_pillow)

                # リクエスト処理
                api_msg = {'image': img_base64}
                #api_msg = json.dumps(api_msg)  # Fast API では、json.dump() で dict 型データを JSON 形式に変換する必要はない

                try:
                    api_responce = requests.post( "http://" + args.host + ":" + args.port + "/predict", json=api_msg )
                    api_responce = api_responce.json()
                except Exception as e:
                    print( "Exception : ", e )
                    time.sleep(1)
                    continue

                if( api_responce["status"] == "ok" ):
                    img_out_pillow = conv_base64_to_pillow(api_responce["img_base64"])
                    img_out_pillow.save(os.path.join(args.out_images_dir,img_name))
                    
            #----------------------------------
            # ログデータ取得
            #----------------------------------
            log_json = requests.get( "http://" + args.host + ":" + args.port + "/log_all" ).json()
            print( "log_json : ", log_json )
        ```

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
    ```sh
    $ python request.py --host ${HOST} --port ${PORT} --in_images_dir in_images --out_images_dir out_images --debug
    ```

    `http:0.0.0.0:5000/predict` のエンドポイントに POST リクエストされると Web-API は、自身のログデータを MySQL データベースに書き込む動作になっている。

    `http:0.0.0.0:5000/log_all`, `http:0.0.0.0:5000/log_first` のエンドポイントに GET リクエストされると、Web-API は、MySQL に書き込んだテーブルデータを返す。正常に動作している場合は、MySQL に書き込まれたログデータがレスポンスされる
    ```sh
    [
        {
            "datetime": null,
            "log": {"job_id": "0d622b", "func_name": "predict", "time_stamp": "2021-06-27 16:15:50", "elapsed_time": 12.03012466430664},
            "log_id": "0d622b",
            "registry": null
        },
        {
            "datetime": null, 
            "log": {"job_id": "130e97", "func_name": "predict", "time_stamp": "2021-06-27 16:17:17", "elapsed_time": 12.778282165527344},
            "log_id": "130e97",
            "registry": null
        },
        {
            "datetime": null,
            "log": {"job_id": "1e89cb", "func_name": "predict", "time_stamp": "2021-06-27 16:17:16", "elapsed_time": 24.025917053222656},
            "log_id": "1e89cb",
            "registry": null
        },
        ...
    ```
