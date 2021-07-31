# 入力データや前処理データを Redis にキャッシュし、同じ入力データでの Web-API の推論処理を高速化する（FastAPI + uvicorn + gunicorn + redis + docker + docker-compose での構成）

「[推論結果を Redis にキャッシュし、同じ入力データでの Web-API の推論処理を高速化する（FastAPI + uvicorn + gunicorn + redis + docker + docker-compose での構成）](https://github.com/Yagami360/MachineLearning_Tips/tree/master/ml_ops/39)」では、ある入力画像に対しての推論結果を Redis にキャッシュデータとして保存し、同じ入力画像が入力された場合にそのキャッシュデータをレスポンスすることで、次回から同じ入力画像で推論した場合の処理時間を高速化する方法を記載した。

ここでは、推論結果だけでなく、入力データ（入力画像など）や前処理データ（機械学習APIの場合は、前処理APIでの処理結果や機械学習モデルから抽出した特徴量など）も Redis にキャッシュデータとして保存する方法を記載する。

入力データをキャッシュデータとして保存することで、クライアントから入力データを送信する際の処理時間が大幅に短縮できるメリットがある。

また前処理データをキャッシュデータとして保存することで、同じ入力データに対しての次回からの 前処理 API での処理が不要になり、API全体の処理時間が大幅に短縮できるメリットがある。


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

                # キューに前処理済みのキャッシュデータが存在するか確認
                cache_img_base64 = get_image_base64_redis(redis_client, key_name=img_data.file_path)

                # キューに推論済みのデータが存在しない場合
                if(cache_img_base64 == None):
                    logger.info(f"registering cache: {img_data.file_path}")
                    # 前処理（resize 処理）
                    img_pillow = conv_base64_to_pillow(img_data.img_base64)
                    img_resized_pillow = img_pillow.resize((ProxyServerConfig.image_width,ProxyServerConfig.image_height))
                    cache_img_base64 = conv_pillow_to_base64(img_resized_pillow)

                    # 前処理データをキャッシュに保存
                    task = CacheDataRedisJob(file_name=img_data.file_path, img_base64=cache_img_base64)      # ジョブクラスのオブジェクト作成
                    background_tasks.add_task(task)                                                            # BackgroundTasks にジョブを追加
                else:
                    logger.info(f"cache hit: {img_data.file_path}")

                # Web-API に推論リクエスト
                try:
                    api_responce = requests.post( ProxyServerConfig.predict_server_url + "/predict", json={'image': cache_img_base64}, params={"job_id": job_id} )
                    api_responce = api_responce.json()
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

                elapsed_time = 1000 * (time.time() - start_time)
                logger.info("{} {} {} {} job_id={}, elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", job_id, elapsed_time))
                return responce

            ```

            > ここでは前処理後データの簡単な例として、リクエストされた画像データを resize した画像を前処理後データとして、キャッシュに保存している

            > 前処理後データのキャッシュに保存する処理は、`BackgroundTasks` でバックグラウンド処理で行っている。バックグラウンド処理で行うのは、本来の処理が遅くならないようにするため

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
    2021-07-31 11:08:48 INFO predict START job_id=e150ec
    registering cache: in_images/000001_0.jpg
    2021-07-31 11:08:49 INFO predict END job_id=e150ec, elapsed_time [ms]=1374.10879
    [CacheDataRedisJob] time 11:08:49 | FileName in_images/000001_0.jpg を登録しました
    2021-07-31 11:08:49 INFO predict START job_id=a0375f
    registering cache: in_images/000010_0.jpg
    2021-07-31 11:08:51 INFO predict END job_id=a0375f, elapsed_time [ms]=1889.28747
    [CacheDataRedisJob] time 11:08:51 | FileName in_images/000010_0.jpg を登録しました
    2021-07-31 11:08:51 INFO predict START job_id=c9dd09
    registering cache: in_images/000020_0.jpg
    2021-07-31 11:08:54 INFO predict END job_id=c9dd09, elapsed_time [ms]=2925.02093
    [CacheDataRedisJob] time 11:08:54 | FileName in_images/000020_0.jpg を登録しました
    2021-07-31 11:08:54 INFO predict START job_id=672ba6
    registering cache: in_images/000028_0.jpg
    2021-07-31 11:08:56 INFO predict END job_id=672ba6, elapsed_time [ms]=1189.43858
    [CacheDataRedisJob] time 11:08:56 | FileName in_images/000028_0.jpg を登録しました
    2021-07-31 11:08:56 INFO predict START job_id=265a9c
    registering cache: in_images/000038_0.jpg
    2021-07-31 11:08:57 INFO predict END job_id=265a9c, elapsed_time [ms]=1367.19322
    [CacheDataRedisJob] time 11:08:57 | FileName in_images/000038_0.jpg を登録しました
    ```

    ２回目以降のリクエストに対してのログデータ
    ```sh
    2021-07-31 11:11:43 INFO predict START job_id=64f52e
    cache hit: in_images/000001_0.jpg
    2021-07-31 11:11:45 INFO predict END job_id=64f52e, elapsed_time [ms]=1349.62893
    2021-07-31 11:11:45 INFO predict START job_id=6888c4
    cache hit: in_images/000010_0.jpg
    2021-07-31 11:11:46 INFO predict END job_id=6888c4, elapsed_time [ms]=1622.26868
    2021-07-31 11:11:47 INFO predict START job_id=e1f2de
    cache hit: in_images/000020_0.jpg
    2021-07-31 11:11:49 INFO predict END job_id=e1f2de, elapsed_time [ms]=2817.48772
    2021-07-31 11:11:50 INFO predict START job_id=cf563f
    cache hit: in_images/000028_0.jpg
    2021-07-31 11:11:51 INFO predict END job_id=cf563f, elapsed_time [ms]=1128.52955
    2021-07-31 11:11:51 INFO predict START job_id=bd8a5f
    cache hit: in_images/000038_0.jpg
    2021-07-31 11:11:52 INFO predict END job_id=bd8a5f, elapsed_time [ms]=1283.67472
    ```

    初回のレスポンスでは、前処理後のキャッシュデータが存在しないので前処理が時間がかかっているが、２回目以降のレスポンスに関しては、前処理後のキャッシュデータを使用するので処理が早くなっていることがわかる

## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter4_serving_patterns/data_cache_pattern