# FastAPI を使用した複数の同期処理での Web-API を並列処理する（FastAPI + uvicorn + gunicorn + redis + バッチサーバー + docker での構成）

ここでは、FastAPI で実装した複数の Web-API から構成される Web-API において、`httpx` と `asyncio` モジュールを使用して、各々の Web-API 並列処理する方法を記載する

Web-API 並列処理することで、以下のようなメソッドがある。

- 例えば、３つの推論サーバーがあった場合に、それぞれのサーバーを直列で処理するとトータルでの処理時間は、｛１つ目の推論サーバーの処理時間＋２つ目の推論サーバーの処理時間＋３つ目の推論サーバーの処理時間｝になってしまう。一方これらの３つの推論サーバーを並列処理すれば、最も処理が遅い推論サーバーの処理時間で済み、処理時間を大幅に短くできる
- 特に、機械学習 API では複数の前処理サーバーが必要なケースが多いが、これらの前処理サーバーを並列処理するようにすれば、トータルでの推論時間を大幅に短くすることができる

<img src="https://user-images.githubusercontent.com/25688193/125183134-017a0600-e24f-11eb-8c50-d7cbb8a78857.png" width="500"><br>

## ■ 方法

1. Web-API（推論サーバー）の構築<br>
    1. Web-API（推論サーバー）の API コードを作成する<br>
    1. Web-API（推論サーバー）の Dockerfile を作成する<br>

1. プロキシサーバーの構築<br>
    1. プロキシサーバーの API コードを作成する<br>
        複数の Web-API に対して並列処理でリクエストするためのプロキシサーバーの API コードを作成する<br>
        `httpx` と `asyncio` モジュールを使用して、複数 Web-API を並列処理している点がポイント
        ```python
        import os
        import logging
        from datetime import datetime
        import time
        import asyncio
        import time
        import requests
        import httpx
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

        @app.get("/")
        def root():
            return 'Hello Proxy Server!\n'

        @log_base_decorator(logger=logger)
        def _health():
            try:
                health_predict_server1 = requests.get(ProxyServerConfig.predict_server1_url + "/health").json()
            except Exception as e:
                health_predict_server1 = {"health": "ng"}

            try:
                health_predict_server2 = requests.get(ProxyServerConfig.predict_server2_url + "/health").json()
            except Exception as e:
                health_predict_server2 = {"health": "ng"}

            try:
                health_predict_server3 = requests.get(ProxyServerConfig.predict_server3_url + "/health").json()
            except Exception as e:
                health_predict_server3 = {"health": "ng"}

            return {
                "proxy_server" : {"health": "ok"},
                "predict_server1" : health_predict_server1,
                "predict_server2" : health_predict_server2,
                "predict_server3" : health_predict_server3,
            }

        @app.get("/health")
        def health():
            return _health()

        @app.get("/metadata")
        def metadata():    
            return

        @app.post("/predict")
        async def predict(
            img_data: ImageData,                # リクエストボディ
        ):
            start_time = time.time()

            # job_id を自動生成
            job_id = str(uuid.uuid4())[:6]
            logger.info("{} {} {} {} job_id={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", job_id))

            # base64 
            img_base64 = img_data.image

            # 複数の Web-API に非同期処理でリクエスト
            async with httpx.AsyncClient() as client:
                # リクエスト処理を行うメソッド
                async def request(client, end_point, job_id, img_base64):
                    response = await client.post(f"{end_point}", json={"image": img_base64}, params={"job_id": job_id})
                    return response

                # asyncio.gather() で並列処理
                # 実行される順序は不定になるが、処理した結果については渡した順に返される
                # await 構文を付与することで、全ての並列処理が完了するまで wait するようにする
                tasks = [
                    request(client, ProxyServerConfig.predict_server1_url + "/predict", job_id, img_base64),
                    request(client, ProxyServerConfig.predict_server2_url + "/predict", job_id, img_base64),
                    request(client, ProxyServerConfig.predict_server3_url + "/predict", job_id, img_base64),
                ]
                responses = await asyncio.gather(*tasks)

                results = []
                for response in responses:
                    results.append(response.json())

            elapsed_time = 1000 * (time.time() - start_time)
            logger.info("{} {} {} {} job_id={}, elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", job_id, elapsed_time))
            return results
        ```

        ポイントは、以下の通り

        - python3 の `asyncio` モジュールの機能である async def を使用して GET, POST などの関数を定義する。ここで、async def 単体では、非同期処理（マルチスレッド処理）にはならないことに注意。

            <!--
            > `async` 構文 : コルーチン

            > `await` 構文 : 並列処理のタスクが完了するまで待つ
            -->

        - `async with httpx.AsyncClient() as client:` with 構文内の `client.post()` で、Web-API に対して非同期処理でリクエストする

            > `await` を付与することで、

        - `asyncio.gather()` で並列処理を行う。このとき `await` を付与して、全ての並列処理が完了するまで wait するようにする。

            > 全ての並列処理が完了するまで wait するので、最も処理が遅い Web-API に引っ張られて処理時間が遅くなることに注意


    1. プロキシサーバーの Dockerfile を作成する

        > `httpx` モジュールのインストール処理を追加している

1. `docker-compose.yml` を作成する
    ```yml
    version: '2.3'

    services:
    predict_server1:
        container_name: predict-container1
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
            BINARY_THRESHOLD: "240"
        command: bash -c "gunicorn app:app --bind 0.0.0.0:5001 -w 1 -k uvicorn.workers.UvicornWorker --reload"

    predict_server2:
        container_name: predict-container2
        image: predict-image
        build:
            context: "predict/"
            dockerfile: Dockerfile
        volumes:
            - ${PWD}/predict:/predict
            - ${PWD}/utils:/utils
            - ${PWD}/config:/config
        ports:
            - "5002:5002"
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
            BINARY_THRESHOLD: "245"
        command: bash -c "gunicorn app:app --bind 0.0.0.0:5002 -w 1 -k uvicorn.workers.UvicornWorker --reload"

    predict_server3:
        container_name: predict-container3
        image: predict-image
        build:
            context: "predict/"
            dockerfile: Dockerfile
        volumes:
            - ${PWD}/predict:/predict
            - ${PWD}/utils:/utils
            - ${PWD}/config:/config
        ports:
            - "5003:5003"
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
            BINARY_THRESHOLD: "250"
        command: bash -c "gunicorn app:app --bind 0.0.0.0:5003 -w 1 -k uvicorn.workers.UvicornWorker --reload"

    proxy_server:
        container_name: proxy-container
        image: proxy-image
        build:
            context: "proxy/"
            dockerfile: Dockerfile
        volumes:
            - ${PWD}/proxy:/proxy
            - ${PWD}/utils:/utils
            - ${PWD}/config:/config
        ports:
            - "5000:5000"
        tty: true
        depends_on:
            - predict_server1
            - predict_server2
            - predict_server3
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
            PREDICT_SERVER1_URL: "http://predict-container1:5001"
            PREDICT_SERVER2_URL: "http://predict-container2:5002"
            PREDICT_SERVER3_URL: "http://predict-container3:5003"
        command: bash -c "gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"
    ```

1. リクエスト処理のコードを作成する<br>

1. API を起動する<br>
    ```sh
    $ docker-compose -f docker-compose.yml stop
    $ docker-compose -f docker-compose.yml up -d
    ```

1. リクエスト処理を行う<br>
    ```sh
    $ python request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR}
    ```


1. ログファイルを確認する
    プロキシサーバーのログファイル
    ```sh
    2021-07-11 13:28:36 INFO _health START args=() kwds={}
    2021-07-11 13:28:36 INFO _health END elapsed_time [ms]=30.51567, return {'proxy_server': {'health': 'ok'}, 'predict_server1': {'health': 'ok'}, 'predict_server2': {'health': 'ok'}, 'predict_server3': {'health': 'ok'}}
    2021-07-11 13:28:36 INFO predict START job_id=6a10a0
    2021-07-11 13:28:38 INFO predict END job_id=6a10a0, elapsed_time [ms]=1942.11960
    2021-07-11 13:28:38 INFO predict START job_id=552b23
    2021-07-11 13:28:39 INFO predict END job_id=552b23, elapsed_time [ms]=1530.52330
    2021-07-11 13:28:39 INFO predict START job_id=305f14
    2021-07-11 13:28:42 INFO predict END job_id=305f14, elapsed_time [ms]=2549.56651
    2021-07-11 13:28:42 INFO predict START job_id=a010b1
    2021-07-11 13:28:44 INFO predict END job_id=a010b1, elapsed_time [ms]=1859.64608
    2021-07-11 13:28:44 INFO predict START job_id=ac60ee
    2021-07-11 13:28:46 INFO predict END job_id=ac60ee, elapsed_time [ms]=2002.44689
    ```

    推論サーバーのログファイル
    ```sh
    [app] time 13:28:30 | 推論サーバーを起動しました
    [app] time 13:28:30 | 推論サーバーを起動しました
    [app] time 13:28:30 | 推論サーバーを起動しました
    2021-07-11 13:28:36 INFO _health START args=() kwds={}
    2021-07-11 13:28:36 INFO _health END elapsed_time [ms]=0.62203, return {'health': 'ok'}
    2021-07-11 13:28:36 INFO _health START args=() kwds={}
    2021-07-11 13:28:36 INFO _health END elapsed_time [ms]=8.11100, return {'health': 'ok'}
    2021-07-11 13:28:36 INFO _health START args=() kwds={}
    2021-07-11 13:28:36 INFO _health END elapsed_time [ms]=1.22690, return {'health': 'ok'}
    2021-07-11 13:28:36 INFO predict START job_id=6a10a0
    2021-07-11 13:28:36 INFO predict START job_id=6a10a0
    2021-07-11 13:28:36 INFO predict START job_id=6a10a0
    2021-07-11 13:28:37 INFO predict END job_id=6a10a0, elapsed_time [ms]=1637.89678
    2021-07-11 13:28:37 INFO predict END job_id=6a10a0, elapsed_time [ms]=1649.23334
    2021-07-11 13:28:38 INFO predict END job_id=6a10a0, elapsed_time [ms]=1889.82320
    2021-07-11 13:28:38 INFO predict START job_id=552b23
    2021-07-11 13:28:38 INFO predict START job_id=552b23
    2021-07-11 13:28:38 INFO predict START job_id=552b23
    2021-07-11 13:28:39 INFO predict END job_id=552b23, elapsed_time [ms]=1005.13935
    2021-07-11 13:28:39 INFO predict END job_id=552b23, elapsed_time [ms]=1402.17137
    2021-07-11 13:28:39 INFO predict END job_id=552b23, elapsed_time [ms]=1505.75542
    2021-07-11 13:28:40 INFO predict START job_id=305f14
    2021-07-11 13:28:40 INFO predict START job_id=305f14
    2021-07-11 13:28:40 INFO predict START job_id=305f14
    2021-07-11 13:28:42 INFO predict END job_id=305f14, elapsed_time [ms]=2105.92198
    2021-07-11 13:28:42 INFO predict END job_id=305f14, elapsed_time [ms]=2308.70271
    2021-07-11 13:28:42 INFO predict END job_id=305f14, elapsed_time [ms]=2510.82730
    2021-07-11 13:28:42 INFO predict START job_id=a010b1
    2021-07-11 13:28:42 INFO predict START job_id=a010b1
    2021-07-11 13:28:42 INFO predict START job_id=a010b1
    2021-07-11 13:28:44 INFO predict END job_id=a010b1, elapsed_time [ms]=1691.13374
    2021-07-11 13:28:44 INFO predict END job_id=a010b1, elapsed_time [ms]=1793.39886
    2021-07-11 13:28:44 INFO predict END job_id=a010b1, elapsed_time [ms]=1839.49661
    2021-07-11 13:28:44 INFO predict START job_id=ac60ee
    2021-07-11 13:28:44 INFO predict START job_id=ac60ee
    2021-07-11 13:28:44 INFO predict START job_id=ac60ee
    2021-07-11 13:28:46 INFO predict END job_id=ac60ee, elapsed_time [ms]=1778.54109
    2021-07-11 13:28:46 INFO predict END job_id=ac60ee, elapsed_time [ms]=1881.59990
    2021-07-11 13:28:46 INFO predict END job_id=ac60ee, elapsed_time [ms]=1939.89062
    ```

    並列処理を行った結果、プロキシサーバーの処理時間が３つの推論サーバーの和ではなく、３つの推論サーバーのうち最も処理が遅いサーバーの処理時間と同じくくらいになっていることがわかる


## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter4_serving_patterns/horizontal_microservice_pattern
