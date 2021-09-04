# FastAPI を使用した非同期処理での Web-API の構築（FastAPI + uvicorn + gunicorn + redis + バッチサーバー + docker での構成で画像データを扱うケース）

「[FastAPI での非同期処理（FastAPI + uvicorn + gunicorn + docker での構成）](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/35)」記載の方法をベースに、更に以下のコンポーネントや機能を追加することで、非同期処理での WebAPI を構成する

- プロキシサーバー（uvicorn + gunicorn + FastAPI）
    - 非同期処理を行うジョブを定義
- redis サーバー
    - redis をジョブキューとして使用。
- バッチサーバー（＝ジョブの投入から終了までを管理するサーバー）
    - redis のジョブキューを定期的にポーリングして、キューにデータが存在すれば推論サーバーにリクエストする。推論サーバーからのレスポンスデータを redis にレスポンスデータを保存する
- 推論サーバー
    - API の本来の処理を行うサーバー。
    ここでは、簡単のため推論サーバーとして OpenCV の `cv2.grabCut()` を用いた画像の背景除去を使用しているが、機械学習 API の場合は、この推論サーバーの部分が機械学習モデル（画像分類モデルや image-to-image モデルなど）の推論処理になる

## ■ API 構成図
<img src="https://user-images.githubusercontent.com/25688193/121532869-b8117d80-ca3a-11eb-9860-5c7b4f28fcab.png" width="1000"><br>

<img src="https://user-images.githubusercontent.com/25688193/121330685-342f9680-c951-11eb-9036-dcac39a4e5df.png" width="800"><br>

## ■ 使用法

1. redis サーバーのコードを作成する<br>
    例えば以下のような Redis サーバーに接続するためのコードを作成する
    ```python
    import os
    import redis

    import sys
    sys.path.append(os.path.join(os.getcwd(), '../config'))
    from config import ResidConfig

    # Redis サーバーに接続
    redis_client = redis.Redis(host=ResidConfig.host, port=ResidConfig.port, db=ResidConfig.database_id)
    ```

1. プロキシサーバーのコードを作成する<br>
    FastAPI を用いて、例えば以下のようなプロキシサーバーのコードを作成する。<br>
    ジョブクラスの処理にて、Redis に job_id のキューデータと、入力画像の文字列型データを保存いている点がポイント

    ```python
    import os
    import logging
    from datetime import datetime
    from time import sleep
    import asyncio
    import redis
    import uuid
    from PIL import Image

    from fastapi import FastAPI
    from fastapi import BackgroundTasks
    from pydantic import BaseModel
    from typing import Any, Dict

    import sys
    sys.path.append(os.path.join(os.getcwd(), '../redis'))
    from redis_client import redis_client
    from redis_utils import set_image_pillow_redis, set_image_base64_redis, get_image_pillow_redis, get_image_base64_redis

    sys.path.append(os.path.join(os.getcwd(), '../utils'))
    from utils import conv_base64_to_pillow, conv_pillow_to_base64

    app = FastAPI()

    # logger
    if( os.path.exists(__name__ + '.log') ):
        os.remove(__name__ + '.log')
    logger = logging.getLogger(__name__)
    logger.setLevel(10)
    logger_fh = logging.FileHandler(__name__ + '.log')
    logger.addHandler(logger_fh)

    class ImageData(BaseModel):
        """
        画像データのリクエストボディ
        """
        image: Any

    class SetDataRedisJob(BaseModel):
        """
        非同期処理での Job を定義したジョブクラス
        """
        job_id: str
        img_base64: Any
        job_status: str = "RUNNING"

        def __call__(self):
            jobs[self.job_id] = self
            self.job_status = "RUNNING"
            try:
                # Redis キューの先頭に job_id を追加
                redis_client.lpush("job_id", self.job_id)
                print('[{}] time {} | Job {} を登録しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))
                logger.info('[{}] time {} | Job {} を登録しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))

                # 画像を追加
                set_image_base64_redis(redis_client=redis_client, key_name=self.job_id+"_image_in", img_base64=self.img_base64)

                self.job_status = "SUCCEED"
            except Exception:
                print('[{}] time {} | Job {} の登録に失敗しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))
                logger.info('[{}] time {} | Job {} の登録に失敗しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))
                self.job_status = "FAILED"

            return

    jobs : Dict[str, SetDataRedisJob] = {}

    @app.get("/")
    async def root():
        return 'Hello Proxy Server!\n'

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/metadata")
    async def metadata():    
        return {
            "status": "ok",
            "jobs" : jobs,
            "job_id_redis" : redis_client.lrange("job_id",0,-1),
        }

    @app.get("/get_job/{job_id}")
    async def get_job(
        job_id: str,  # パスパラメーター
    ):
        status = "ok"
        try:
            img_in_base64 = get_image_base64_redis( redis_client=redis_client, key_name=job_id+"_image_in" )
        except Exception:
            img_in_base64 = None
            status = "ng"
        try:
            img_out_base64 = get_image_base64_redis( redis_client=redis_client, key_name=job_id+"_image_out" )
        except Exception:
            img_out_base64 = None
            status = "ng"

        return {
            "status": status,
            "job_id" : jobs[job_id].job_id,
            "job_status" : jobs[job_id].job_status,
            "img_in_base64" : img_in_base64,
            "img_out_base64" : img_out_base64,
        }

    @app.post("/start_job")
    async def start_job(
        img_data: ImageData,                # リクエストボディ
        background_tasks: BackgroundTasks,  # BackgroundTasks
    ):
        # job_id を自動生成
        job_id = str(uuid.uuid4())[:6]

        # ジョブクラスのオブジェクト作成
        task = SetDataRedisJob(job_id=job_id, img_base64=img_data.image)

        # BackgroundTasks にジョブを追加
        background_tasks.add_task(task)

        return {
            "status": "ok",
            "job_id" : task.job_id,
            "job_status" : task.job_status,
        }
    ```

1. バッチサーバーのコードを作成する<br>
    バッチサーバーでは、Redis のデータを定期的にポーリングし、データがあれば推論サーバーにリクエスト処理する。
    その後、推論サーバーからのレスポンスデータを Redis に保存する。

    バッチサーバーでのポーリング処理は、`asyncio` と `concurrent.futures.ProcessPoolExecutor` を使用した並列処理で行う。

    ```python
    import os
    import logging
    from datetime import datetime
    from time import sleep
    from concurrent.futures import ProcessPoolExecutor
    import asyncio
    import requests

    import sys
    sys.path.append(os.path.join(os.getcwd(), '../config'))
    from config import BatchServerConfig
    from config import PredictServerConfig

    sys.path.append(os.path.join(os.getcwd(), '../redis'))
    from redis_client import redis_client
    from redis_utils import set_image_pillow_redis, set_image_base64_redis, get_image_pillow_redis, get_image_base64_redis

    sys.path.append(os.path.join(os.getcwd(), '../utils'))
    from utils import conv_base64_to_pillow, conv_pillow_to_base64

    # logger
    if( os.path.exists(__name__ + '.log') ):
        os.remove(__name__ + '.log')
    logger = logging.getLogger(__name__)
    logger.setLevel(10)
    logger_fh = logging.FileHandler( __name__ + '.log')
    logger.addHandler(logger_fh)

    def polling():
        """
        Redis のキューを定期的にポーリングして、API サーバーにリクエスト処理を送信する
        """
        while True:
            # Redis キューの末端からデータを pop
            job_id = redis_client.rpop('job_id')
            print('[{}] time {} | Job {} を pop しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id))
            logger.info('[{}] time {} | Job {} を pop しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id))

            if job_id is not None:
                job_id = job_id.decode()
                
                # job_id に対応した 画像データを取得
                img_base64 = get_image_base64_redis( redis_client=redis_client, key_name=job_id+"_image_in" )

                # 推論サーバーのヘルスチェック
                try:
                    health = requests.get( "http://" + PredictServerConfig.host + ":" + PredictServerConfig.port + "/health" ).json()
                    print( "health : ", health )
                    logger.info('[{}] time {} | health {}'.format(__name__, f"{datetime.now():%H:%M:%S}", health))
                except Exception as e:
                    print( "Exception : ", e )
                    logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))

                # 推論サーバーにリクエスト処理
                try:
                    api_msg = {'image': img_base64}
                    api_responce = requests.post( "http://" + PredictServerConfig.host + ":" + PredictServerConfig.port + "/predict", json=api_msg )
                    api_responce = api_responce.json()
                    logger.info('[{}] time {} | api_responce["status"] {}'.format(__name__, f"{datetime.now():%H:%M:%S}", api_responce["status"]))
                except Exception as e:
                    print( "Exception : ", e )
                    logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))

                # Redis の画像データに登録
                set_image_base64_redis( redis_client=redis_client, key_name=job_id+"_image_out", img_base64=api_responce["img_none_bg_base64"])

            # ポーリング間隔
            sleep(BatchServerConfig.polling_time)

        return

    if __name__ == "__main__":
        executor = ProcessPoolExecutor(BatchServerConfig.n_workers)
        loop = asyncio.get_event_loop()

        for _ in range(BatchServerConfig.n_workers):
            # loop.run_in_executor() により、実際の処理 _loop() を別スレッドで実行するコルーチンがを生成
            # 作成したコルーチンを asyncio.ensure_future で Task 化
            # executor として、デフォルトの ThreadPoolExecutor ではなく ProcessPoolExecutor を使用
            asyncio.ensure_future(loop.run_in_executor(executor, polling))

        # loop.stop()が呼ばれるまでループし続ける
        loop.run_forever()
    ```

1. 推論サーバーのコードを作成する<br>
    ここでは例えば、OpenCV の `cv2.grabCut()` を用いた推論サーバーを構築する。
    機械学習 API の場合は、この推論サーバーの部分が機械学習モデルを使用した推論処理になる。

    ```python
    import os
    import asyncio
    from datetime import datetime
    from time import sleep
    import logging

    from fastapi import FastAPI
    from pydantic import BaseModel
    from typing import Any, Dict

    from api_utils import graph_cut

    import sys
    sys.path.append(os.path.join(os.getcwd(), '../utils'))
    from utils import conv_base64_to_pillow, conv_pillow_to_base64

    # logger
    if( os.path.exists(__name__ + '.log') ):
        os.remove(__name__ + '.log')
    logger = logging.getLogger(__name__)
    logger.setLevel(10)
    logger_fh = logging.FileHandler( __name__ + '.log')
    logger.addHandler(logger_fh)

    app = FastAPI()
    print('[{}] time {} | 推論サーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    logger.info('[{}] time {} | 推論サーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

    class ImageData(BaseModel):
        """
        画像データのリクエストボディ
        """
        image: Any

    @app.get("/")
    async def root():
        return 'Hello API Server!\n'

    @app.get("/health")
    async def health():
        return {"health": "ok"}

    @app.get("/metadata")
    async def metadata():
        return

    @app.post("/predict")
    async def predict(
        img_data: ImageData,        # リクエストボディ    
    ):
        print('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
        logger.info('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

        # base64 -> Pillow への変換
        img_data.image = conv_base64_to_pillow(img_data.image)

        # OpenCV を用いて背景除去
        _, img_none_bg_pillow = graph_cut(img_data.image)

        # Pillow -> base64 への変換
        img_none_bg_base64 = conv_pillow_to_base64(img_none_bg_pillow)

        # 非同期処理の効果を明確化するためにあえて sleep 処理
        sleep(1)

        # レスポンスデータ設定
        print('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
        logger.info('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

        return {
            "status": "ok",
            "img_none_bg_base64" : img_none_bg_base64,
        }
    ```

1. docker-compose で API を構成する<br>
    プロキシサーバー・Redis サーバー・バッチサーバー・推論サーバーを docker-compose で構築する。
    ```python
    version: '2.3'

    services:
        predict_server:
        container_name: predict-container
        image: predict-image
        build:
            context: "predict/"
            dockerfile: Dockerfile
        volumes:
            - ${PWD}/predict:/predict
            - ${PWD}/utils:/utils
            - ${PWD}/config:/config
        ports:
            - "5001:5001"
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
        command: bash -c "gunicorn app:app --bind 0.0.0.0:5001 -w 1 -k uvicorn.workers.UvicornWorker --reload"

        redis_server:
        container_name: redis-container
        image: redis:latest
        ports:
            - "6379:6379"
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
        command: bash -c "redis-server"

        batch_server:
        container_name: batch-container
        image: batch-image
        build:
            context: "batch/"
            dockerfile: Dockerfile
        volumes:
            - ${PWD}/batch:/batch
            - ${PWD}/redis:/redis
            - ${PWD}/utils:/utils
            - ${PWD}/config:/config
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
        command: bash -c "python batch_server.py"
        depends_on:
            - redis_server
            - predict_server

        proxy_server:
        container_name: proxy-container
        image: proxy-image
        build:
            context: "proxy/"
            dockerfile: Dockerfile
        volumes:
            - ${PWD}/proxy:/proxy
            - ${PWD}/redis:/redis
            - ${PWD}/utils:/utils
            - ${PWD}/config:/config
        ports:
            - "5000:5000"
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
        command: bash -c "gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"
        depends_on:
            - redis_server
            - batch_server
            - predict_server
    ```

1. リクエスト処理のコードを作成する<br>
    `requests` モジュールを用いて、例えば以下のようなリクエスト処理のコードを作成する。
    
    > リクエスト処理を `curl` コマンドで直接行う場合は、リクエスト処理のコードは不要

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
    from utils.utils import conv_base64_to_pillow, conv_pillow_to_base64

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
        parser.add_argument('--n_pollings', type=int, default=100, help="ポーリング回数")
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
        # ジョブ開始
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
                api_responce = requests.post( "http://" + args.host + ":" + args.port + "/start_job", json=api_msg )
                api_responce = api_responce.json()
                print( "api_responce : ", api_responce )
            except Exception as e:
                print( "Exception : ", e )
                time.sleep(1)
                continue

            job_id = api_responce["job_id"]
            job_status = api_responce["job_status"]
            print( "img_name={}, job_id={}, job_status={}".format(img_name, job_id, job_status) )
            job_ids.append(job_id)

            # 
            time.sleep(0.1)

        #----------------------------------
        # job の確認
        #----------------------------------
        for n_polling in tqdm(range(args.n_pollings)):
            if(len(job_ids)==0):
                break
            for i,job_id in enumerate(job_ids):
                job_data = requests.get( "http://" + args.host + ":" + args.port + "/get_job/" + job_id ).json()
                if( job_data["status"] == "ok" ):
                    img_out_pillow = conv_base64_to_pillow(job_data["img_out_base64"])
                    img_out_pillow.save(os.path.join(args.out_images_dir,job_data["job_id"]+".png"))
                    job_ids.remove(job_id)

            time.sleep(1)
    ```

    > `requests` モジュールを用いて POST メリットでリクエストボディ（jsonデータ）を送信する際に、Flask では `json.dumps()` を用いて dict 型データを JSON 形式に変換する必要する必要があったが、FastAPI では、`json.dumps()` を行う必要がないことに注意

1. API を起動する<br>
    ```sh
    $ docker-compose -f docker-compose.yml stop
    $ docker-compose -f docker-compose.yml up -d
    ```

1. リクエスト処理する<br>
    上記作成したリクエスト処理のコードを用いてリクエスト処理する場合は、以下のコマンドを実行する
    ```sh
    $ python request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR}
    ```

<!--
    `curl` コマンドでリクエスト処理する場合は、以下のコマンドを実行する
    ```sh
    # ヘルスチェック
    $ curl http://${HOST}:${PORT}/health
    ```

    ```sh
    # リクエスト処理
    $ IMAGE_BASE64=`base64 in_images/000001_0.jpg`
    $ curl -X POST \
        -H "Content-Type: application/json" \
        -d "{'image': ${IMAGE_BASE64}}" \
        http://${HOST}:${PORT}/start_job
    ```
-->

## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter4_serving_patterns/asynchronous_pattern
- https://qiita.com/icoxfog417/items/07cbf5110ca82629aca0