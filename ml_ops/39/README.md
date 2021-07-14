# 推論結果を Redis にキャッシュし、同じ入力データでの Web-API の推論処理を高速化する（FastAPI + uvicorn + gunicorn + redis + docker + docker-compose での構成）

ここでは、Web-API に入力された画像での処理結果画像を Redis にキャッシュデータとして保存し、同じ入力画像が入力された場合にそのキャッシュデータをレスポンスすることで、次回から同じ入力画像で推論した場合のの処理時間を高速化する方法を記載する。

機械学習 API においては、推論処理が長いことが問題になるケースが多いが、同じ入力データで繰り返し推論するシステムの場合は、予めその入力データで推論し推論結果をキャッシュしておくことで、そのデータでの推論時間を高速化できるようになる。

> 尚、ここでは同じ入力画像が入力されたかの判別をファイル名から行っている。そのため、異なる入力画像でもファイル名が同じであれば、同じ入力データとしてキャッシュしてしまう。予めキャッシュ対象の入力画像ファイルが定まってる場合は、ファイル名がかぶらないように、UUID などの一意のファイル名にすることで、この問題を回避できる

<img src="https://user-images.githubusercontent.com/25688193/125589979-8188d38a-6f41-4e66-aa2c-d914d26047d2.png" width="500"><br>

<img src="https://user-images.githubusercontent.com/25688193/125590038-f77cd203-cab3-4060-8c66-667925189ab1.png" width="500"><br>

<img src="" width="500"><br>

## ■ 方法

1. 推論サーバーの構築<br>
    1. 推論サーバーのコードを作成する<br>

        - `app.py`
            ```python
            ```

    1. 推論サーバーの Dockerfile を作成する<br>
        ```dockerfile
        ```

1. Redis サーバーの構築
    1. Redis サーバーのコードを作成する<br>
        - `redis_client.py`<br>
            ```python
            ```

        - `redis_utils.py` : Redis のキューデータにアクセスするための utils 群モジュール<br>
            ```python
            ```

1. プロキシサーバーの構築<br>
    1. プロキシサーバーのコードを作成する<br>
        - `app.py`
            ```python
            import os
            import logging
            from datetime import datetime
            import time
            import asyncio
            import time
            import requests
            import uuid
            from PIL import Image

            from fastapi import FastAPI
            from fastapi import BackgroundTasks
            from pydantic import BaseModel
            from typing import Any, Dict

            import sys
            sys.path.append(os.path.join(os.getcwd(), '../'))
            from config.config import ProxyServerConfig
            from utils.utils import conv_base64_to_pillow, conv_pillow_to_base64
            from utils.logger import log_base_decorator, log_decorator

            sys.path.append(os.path.join(os.getcwd(), '../redis'))
            from redis_client import redis_client
            from redis_utils import set_image_pillow_redis, set_image_base64_redis, get_image_pillow_redis, get_image_base64_redis

            app = FastAPI()

            # logger
            """
            if( os.path.exists(__name__ + '.log') ):
                os.remove(__name__ + '.log')
            """
            logger = logging.getLogger(__name__)
            logger.setLevel(10)
            logger_fh = logging.FileHandler(__name__ + '.log')
            logger.addHandler(logger_fh)


            class ImageData(BaseModel):
                """
                画像データのリクエストボディ
                """
                file_path: str
                img_base64: Any

            class CacheDataRedisJob(BaseModel):
                """
                バックグラウンドで推論データのキャッシュを Redis に保存するための Job
                """
                file_name: str
                img_base64: Any

                def __call__(self):
                    jobs[self.file_name] = self
                    try:
                        # Redis キューの先頭に file_name:img_base64 のキーデータを追加
                        redis_client.lpush("file_name", self.file_name)
                        print('[{}] time {} | FileName {} を登録しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.file_name))
                        logger.info('[{}] time {} | FileName {} を登録しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.file_name))

                        # 画像を追加
                        set_image_base64_redis(redis_client=redis_client, key_name=self.file_name, img_base64=self.img_base64)

                    except Exception:
                        print('[{}] time {} | FileName {} の登録に失敗しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.file_name))
                        logger.info('[{}] time {} | FileName {} の登録に失敗しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.file_name))

                    return

            jobs : Dict[str, CacheDataRedisJob] = {}

            @app.get("/")
            def root():
                return 'Hello Proxy Server!\n'

            @log_base_decorator(logger=logger)
            def _health():
                try:
                    health_predict_server = requests.get(ProxyServerConfig.predict_server_url + "/health").json()
                except Exception as e:
                    health_predict_server = {"health": "ng"}

                return {
                    "proxy_server" : {"health": "ok"},
                    "predict_server" : health_predict_server,
                }

            @app.get("/health")
            def health():
                return _health()

            @app.get("/metadata")
            def metadata():    
                return

            @app.post("/predict")
            def predict(
                img_data: ImageData,                # リクエストボディ
                background_tasks: BackgroundTasks,  # BackgroundTasks
            ):
                start_time = time.time()

                # job_id を自動生成
                job_id = str(uuid.uuid4())[:6]
                logger.info("{} {} {} {} job_id={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", job_id))

                # キューに推論済みのキャッシュデータが存在するか確認
                cache_img_base64 = get_image_base64_redis(redis_client, key_name=img_data.file_path)

                # キューに推論済みのデータが存在しない場合
                if(cache_img_base64 == None):
                    logger.info(f"registering cache: {img_data.file_path}")

                    # Web-API に推論リクエスト
                    try:
                        api_responce = requests.post( ProxyServerConfig.predict_server_url + "/predict", json={'image': img_data.img_base64}, params={"job_id": job_id} )
                        api_responce = api_responce.json()

                        # 推論データをキャッシュに保存
                        task = CacheDataRedisJob(file_name=img_data.file_path, img_base64=api_responce["img_none_bg_base64"])      # ジョブクラスのオブジェクト作成
                        background_tasks.add_task(task)                                                                            # BackgroundTasks にジョブを追加

                        responce = {
                            "status" : "ok",
                            "img_none_bg_base64" : api_responce["img_none_bg_base64"],
                        }

                    except Exception as e:
                        print( "Exception : ", e )
                        logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))
                        responce = {
                            "status" : "ng",
                            "img_none_bg_base64" : None,
                        }
                else:
                    logger.info(f"cache hit: {img_data.file_path}")
                    responce = {
                        "status" : "ok",
                        "img_none_bg_base64" : cache_img_base64,
                    }

                elapsed_time = 1000 * (time.time() - start_time)
                logger.info("{} {} {} {} job_id={}, elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", job_id, elapsed_time))
                return responce

            ```

            > 推論データのキャッシュに保存する処理は、`BackgroundTasks` でバックグラウンド処理で行っている。バックグラウンド処理で行うのは、本来の処理が遅くならないようにするため

            > Redis のキューデータには、画像ファイル名を key として、base64 形式の画像データが保管される

    1. プロキシサーバーの Dockerfile を作成する<br>
        ```dockerfile
        ```

1. `docker-compose.yml` を作成する<br>
    プロキシサーバー・Redis サーバー・推論サーバーから構成される Web-API の docker-compose を作成する<br>
    ```yml
    ```

    > redis の docker image は、`redis:latest` を使用する

1. リクエスト処理のコードを作成する
    - `request.py`
        ```python
        ```

1. API を起動する
    ```sh
    $ docker-compose -f docker-compose.yml stop
    $ docker-compose -f docker-compose.yml up -d
    ```

1. リクエスト処理する
    ```sh
    $ python request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR}
    ```

    １回目のリクエストに対してのログデータ
    ```sh
    2021-07-11 18:43:01 INFO predict START job_id=f3d237
    registering cache: in_images/000001_0.jpg
    2021-07-11 18:43:02 INFO predict END job_id=f3d237, elapsed_time [ms]=445.93096
    [CacheDataRedisJob] time 18:43:02 | FileName in_images/000001_0.jpg を登録しました
    2021-07-11 18:43:02 INFO predict START job_id=77e8de
    registering cache: in_images/000010_0.jpg
    2021-07-11 18:43:02 INFO predict END job_id=77e8de, elapsed_time [ms]=258.72540
    [CacheDataRedisJob] time 18:43:02 | FileName in_images/000010_0.jpg を登録しました
    2021-07-11 18:43:02 INFO predict START job_id=a39dde
    registering cache: in_images/000020_0.jpg
    2021-07-11 18:43:03 INFO predict END job_id=a39dde, elapsed_time [ms]=910.98833
    [CacheDataRedisJob] time 18:43:03 | FileName in_images/000020_0.jpg を登録しました
    2021-07-11 18:43:03 INFO predict START job_id=85f054
    registering cache: in_images/000028_0.jpg
    2021-07-11 18:43:04 INFO predict END job_id=85f054, elapsed_time [ms]=234.86805
    [CacheDataRedisJob] time 18:43:04 | FileName in_images/000028_0.jpg を登録しました
    2021-07-11 18:43:04 INFO predict START job_id=35f7e0
    registering cache: in_images/000038_0.jpg
    2021-07-11 18:43:04 INFO predict END job_id=35f7e0, elapsed_time [ms]=243.07585
    [CacheDataRedisJob] time 18:43:04 | FileName in_images/000038_0.jpg を登録しました
    ```

    ２回目以降のリクエストに対してのログデータ
    ```sh
    2021-07-11 18:45:32 INFO predict START job_id=25e4a7
    cache hit: in_images/000001_0.jpg
    2021-07-11 18:45:32 INFO predict END job_id=25e4a7, elapsed_time [ms]=4.23503
    2021-07-11 18:45:32 INFO predict START job_id=bb2678
    cache hit: in_images/000010_0.jpg
    2021-07-11 18:45:32 INFO predict END job_id=bb2678, elapsed_time [ms]=3.52383
    2021-07-11 18:45:32 INFO predict START job_id=f06154
    cache hit: in_images/000020_0.jpg
    2021-07-11 18:45:32 INFO predict END job_id=f06154, elapsed_time [ms]=2.47335
    2021-07-11 18:45:32 INFO predict START job_id=66919a
    cache hit: in_images/000028_0.jpg
    2021-07-11 18:45:32 INFO predict END job_id=66919a, elapsed_time [ms]=1.70183
    2021-07-11 18:45:32 INFO predict START job_id=e4599e
    cache hit: in_images/000038_0.jpg
    2021-07-11 18:45:32 INFO predict END job_id=e4599e, elapsed_time [ms]=3.32642
    ```

    初回のレスポンスでは、キャッシュデータが存在しないので、推論 API で推論を行い処理に時間がかかっているが、２回目以降のレスポンスに関しては、キャッシュデータを使用するので処理が早くなっていることがわかる

## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter4_serving_patterns/prediction_cache_pattern