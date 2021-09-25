# FastAPI を使用した非同期処理での Web-API の構築（FastAPI + uvicorn + gunicorn + バッチサーバー + docker での構成で動画データを扱うケース）

「[FastAPI を使用した非同期処理での Web-API の構築（FastAPI + uvicorn + gunicorn + redis + バッチサーバー + docker での構成で画像データを扱うケース）](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/36)」記載の方法では、Redis のキューデータに画像データを保存し、非同期 API を実現していたが、Redis のキューデータ上に大容量の動画データを保存するとメモリを多量に消費してしまい OutOfMemory エラーが発生する懸念がある。

この問題を回避するために、ここでは、以下のような処理を行うことで、動画データに対しての非同期 API を実現する

1. ローカルディスクに job_id のフォルダを作成し、そのディレクトリ以下に動画データを保存する（＝キャッシュデータを保存するディレクトリを使用する）
    ```sh
    +-- /tmp +-- /${JOB_ID}
    |        |   +-- 入力動画ファイル
    |        |   +-- 出力動画ファイル
    ```

1. Redis のキューデータには、job_id とファイルパスのキーデータを保存する。


各コンポーネントの構成は以下のようになる

- プロキシサーバー（uvicorn + gunicorn + FastAPI）<br>
    非同期処理を行うジョブを定義

- redis サーバー<br>
    redis をジョブキューとして使用。

- バッチサーバー（＝ジョブの投入から終了までを管理するサーバー）<br>
    redis のジョブキューを定期的にポーリングして、キューにデータが存在すれば推論サーバーにリクエストする。推論サーバーからのレスポンスデータを redis にレスポンスデータを保存する

- 推論サーバー<br>
    API の本来の処理を行うサーバー。ここでは、簡単のため推論サーバーとして ffppeg を使用した動画の resize を行う処理にしているが、機械学習 API の場合は、この推論サーバーの部分が動画の機械学習モデルの推論処理になる

## ■ API 構成図


## ■ 使用法

1. プロキシサーバーのコードを作成する<br>
    FastAPI を用いて、例えば以下のようなプロキシサーバーのコードを作成する。<br>    
    ```python
    import os
    import logging
    from datetime import datetime
    import time
    import asyncio
    import uuid
    import shutil
    import requests

    from fastapi import FastAPI
    from fastapi import UploadFile, File, HTTPException
    from fastapi.responses import FileResponse
    from fastapi import BackgroundTasks
    from pydantic import BaseModel
    from typing import Any, Dict

    import sys
    sys.path.append(os.path.join(os.getcwd(), '../redis'))
    from redis_client import redis_client

    import sys
    sys.path.append(os.path.join(os.getcwd(), '../config'))
    from config import ProxyServerConfig, PredictServerConfig

    if not os.path.isdir(ProxyServerConfig.cache_dir):
        os.mkdir(ProxyServerConfig.cache_dir)

    # logger
    if not os.path.isdir("log"):
        os.mkdir("log")
    """
    if( os.path.exists(os.path.join("log", 'app.log')) ):
        os.remove(os.path.join("log", 'app.log'))
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(10)
    logger_fh = logging.FileHandler(os.path.join("log", 'app.log'))
    logger.addHandler(logger_fh)
    logger.info("{} {} start proxy-api server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO"))

    # FastAPI
    app = FastAPI()

    class SetDataRedisJob(BaseModel):
        """
        非同期処理での Job を定義したジョブクラス
        """
        job_id: str
        job_status: str = "RUNNING"
        file: UploadFile = File(...)
        file_name: str = None
        file_path: str = None

        def __call__(self):
            jobs[self.job_id] = self
            self.job_status = "RUNNING"
            try:
                # ディスク上に job_id に対応したディレクトリを作成
                if not os.path.isdir( os.path.join(ProxyServerConfig.cache_dir,self.job_id) ):
                    os.mkdir( os.path.join(ProxyServerConfig.cache_dir,self.job_id) )

                # job_id に対応したディレクトリ以下に動画データを保存
                with open(os.path.join(ProxyServerConfig.cache_dir,self.job_id,self.file.filename),'wb+') as buffer:
                    shutil.copyfileobj(self.file.file, buffer)
                self.file_name = self.file.filename
                self.file_path = os.path.join(ProxyServerConfig.cache_dir,self.job_id,self.file.filename)

                # Redis キューの先頭に job_id を追加
                redis_client.lpush("job_id", self.job_id)
                redis_client.set(self.job_id + "_in_file_path", self.file_path)

                logger.info('[{}] time {} | job_id={}, file_path="{}" の動画データを保存しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id, self.file_path))

                self.job_status = "SUCCEED"
            except Exception:
                logger.info('[{}] time {} | job_id={} の動画データの保存に失敗しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))
                self.job_status = "FAILED"

            return

    jobs : Dict[str, SetDataRedisJob] = {}

    @app.get("/")
    async def root():
        return 'Hello Proxy Server!\n'

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/clear_log")
    async def clear_log():
        if( os.path.exists(os.path.join("log", 'app.log')) ):
            os.remove(os.path.join("log", 'app.log'))

        logger_fh = logging.FileHandler(os.path.join("log", 'app.log'))
        logger.addHandler(logger_fh)
        logger.info("{} {} start proxy-api server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO"))

        requests.post( "http://" + PredictServerConfig.host + ":" + PredictServerConfig.port + "/clear_log" )
        return

    @app.post("/clear_cache")
    async def clear_cache():
        shutil.rmtree(ProxyServerConfig.cache_dir)
        if not os.path.isdir(ProxyServerConfig.cache_dir):
            os.mkdir(ProxyServerConfig.cache_dir)

        requests.post( "http://" + PredictServerConfig.host + ":" + PredictServerConfig.port + "/clear_cache" )
        return

    @app.get("/get_job/{job_id}")
    async def get_job(
        job_id: str,  # パスパラメーター
    ):
        try:
            out_file_path = redis_client.get(job_id + "_out_file_path").decode()
            logger.info('[{}] time {} | job_id={}, out_file_path="{}" を get しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id, out_file_path))
        except Exception:
            out_file_path = None
            logger.info('[{}] time {} | job_id={}, out_file_path="{}" を get できません'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id, out_file_path))

        return FileResponse(out_file_path)

    @app.post("/predict")
    async def predict(
        file: UploadFile = File(...),
        background_tasks: BackgroundTasks = None,  # BackgroundTasks
    ):
        # job_id を自動生成
        job_id = str(uuid.uuid4())[:6]
        start_time = time.time()
        logger.info("{} {} {} {} job_id={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", job_id))

        # ジョブクラスのオブジェクト作成
        task = SetDataRedisJob(job_id=job_id, file=file)

        # BackgroundTasks にジョブを追加
        background_tasks.add_task(task)

        elapsed_time = 1000 * (time.time() - start_time)
        logger.info("{} {} {} {} elapsed_time [ms]={:.5f} job_id={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", elapsed_time, job_id))
        return {
            "status": "ok",
            "job_id" : task.job_id,
            "job_status" : task.job_status,
        }
    ```

    ポイントは、以下の通り

    > リクエストされた入力動画を、Redis のキューデータ上にそのまま保存するとメモリを多量に消費してしまい OutOfMemory エラーが発生する懸念があるので、`${JOB_ID}_in_file_path : ${FILE_PATH}` のキーデータを redis に保存している

    > 非同期処理なので、`http://${HOST}:${PORT}/predict` のエンドポイントでは推論処理の成功可否 `status` とジョブ ID `job_id` のみを返しており、推論結果は返していない。推論結果は、上記エンドポイントで得られた `job_id` をもとに `http://${HOST}:${PORT}/get/${JOB_ID}` のエンドポイントで取得できるようにしている

    > `http://${HOST}:${PORT}/get/${JOB_ID}` のエンドポイントでは、`FileResponse()` オブジェクトだけでなく、成功可否ステータス等も dict 型で return したいが、クライアント側で `curl` するとエラーが発生するので、`FileResponse()` オブジェクトだけ return している

    > [ToDo] `http://${HOST}:${PORT}/get/${JOB_ID}` のエンドポイントで、`FileResponse()` オブジェクトだけでなく、成功可否ステータス等も return できるように修正する


1. バッチサーバーのコードを作成する<br>
    バッチサーバーでは、Redis のデータを定期的にポーリングし、データがあれば推論サーバーにリクエスト処理する。
    その後、推論サーバーからのレスポンスデータをローカルディスクのキューデータディレクトリに保存する。

    バッチサーバーでのポーリング処理は、`asyncio` と `concurrent.futures.ProcessPoolExecutor` を使用した並列処理で行う。

    ```python
    import os
    import logging
    from datetime import datetime
    from time import sleep
    from concurrent.futures import ProcessPoolExecutor
    import asyncio
    import requests
    import subprocess

    import sys
    sys.path.append(os.path.join(os.getcwd(), '../redis'))
    from redis_client import redis_client

    sys.path.append(os.path.join(os.getcwd(), '../config'))
    from config import BatchServerConfig
    from config import PredictServerConfig
    from config import ProxyServerConfig

    # logger
    if not os.path.isdir("log"):
        os.mkdir("log")
    """
    if( os.path.exists(os.path.join("log", 'app.log')) ):
        os.remove(os.path.join("log", 'app.log'))
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(10)
    logger_fh = logging.FileHandler(os.path.join("log", 'app.log'))
    logger.addHandler(logger_fh)
    logger.info("{} {} start batch server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO"))

    def polling():
        """
        ローカルディスク上のキャッシュデータを定期的にポーリングして、API サーバーにリクエスト処理を送信する
        """
        while True:
            # Redis キューの末端からデータを pop
            job_id = redis_client.rpop('job_id')
            if job_id is not None:
                job_id = job_id.decode()
                
                # job_id に対応したファイルパスを取得
                in_file_path = redis_client.get(job_id + "_in_file_path").decode()
                logger.info('[{}] time {} | job_id={}, in_file_path="{}" を get しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id, in_file_path))

                # 推論サーバーのヘルスチェック
                try:
                    health = requests.get( "http://" + PredictServerConfig.host + ":" + PredictServerConfig.port + "/health" ).json()
                    logger.info('[{}] time {} | health {}'.format(__name__, f"{datetime.now():%H:%M:%S}", health))
                except Exception as e:
                    logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))

                # 推論サーバーにリクエスト処理
                try:
                    api_responce = requests.post(
                        "http://" + PredictServerConfig.host + ":" + PredictServerConfig.port + "/predict",
                        files={'file': (in_file_path.split("/")[-1], open(in_file_path, "rb"), 'video/mp4')},
                        params={"job_id": job_id},
                    ).json()
                except Exception as e:
                    print( "Exception : ", e )
                    logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))

                # 推論サーバーの処理結果取得
                if( api_responce["status"] == "ok" ):
                    subprocess.call(
                        "curl {} --output {}".format(
                            "http://" + PredictServerConfig.host + ":" + PredictServerConfig.port + "/get_job/" + job_id,
                            os.path.join(ProxyServerConfig.cache_dir, job_id, in_file_path.split(".mp4")[0] + "_out.mp4")
                        ),
                        shell=True,
                    )

                # 出力動画データのファイルパスを保管
                out_file_path = os.path.join(ProxyServerConfig.cache_dir, job_id, in_file_path.split(".mp4")[0] + "_out.mp4" )
                redis_client.set(job_id + "_out_file_path", out_file_path)
                logger.info('[{}] time {} | job_id={}, out_file_path="{}" を set しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id, out_file_path))

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

    ポイントは、以下の通り

    > 推論サーバーの `http://${HOST}:${PORT}/get_job/${JOB_ID}` のエンドポイントでは、`FileResponse()` オブジェクトを return している。このエンドポイントに `requests.get()` でアクセスすると、return された動画ファイルをうまく保存できなかったので、`curl http://${HOST}:${PORT}/get_job/${JOB_ID} --output ${OUTPUT_FILE_PATH}` で動画ファイルを保存している

    > [ToDo] `FileResponse()` オブジェクトを return しているエンドポイント（GET）に対して、`requests.get()` でアクセスした場合でも、出力動画ファイルを保存できるように修正する


1. 推論サーバーのコードを作成する<br>
    ここでは例えば、ffppeg を使用した動画の動画の resize 処理を行う推論サーバーを構築する。
    機械学習 API の場合は、この推論サーバーの部分が機械学習モデルを使用した推論処理になる。

    ```python
    import os
    import asyncio
    from datetime import datetime
    import time
    import logging
    import subprocess
    import shutil

    from fastapi import FastAPI
    from fastapi import UploadFile, File
    from fastapi.responses import FileResponse
    from pydantic import BaseModel
    from typing import Any, Dict

    import sys
    sys.path.append(os.path.join(os.getcwd(), '../config'))
    from config import PredictServerConfig

    if not os.path.isdir(PredictServerConfig.cache_dir):
        os.mkdir(PredictServerConfig.cache_dir)

    # logger
    if not os.path.isdir("log"):
        os.mkdir("log")
    """
    if( os.path.exists(os.path.join("log", 'app.log')) ):
        os.remove(os.path.join("log", 'app.log'))
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(10)
    logger_fh = logging.FileHandler(os.path.join("log", 'app.log'))
    logger.addHandler(logger_fh)
    logger.info("{} {} start predict-api server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO"))

    # FastAPI
    app = FastAPI()
    
    @app.get("/")
    def root():
        return 'Hello API Server!\n'

    @app.get("/health")
    def health():
        return {"health": "ok"}

    @app.get("/metadata")
    def metadata():
        return

    @app.get("/get_job/{job_id}")
    def get_job(
        job_id: str,  # パスパラメーター
    ):
        start_time = time.time()
        file_names = sorted( [f for f in os.listdir(os.path.join(PredictServerConfig.cache_dir, job_id, "out")) if f.endswith(".mp4",".MP4")] )
        logger.info("{} {} {} {} job_id={} file_name={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", job_id, file_names[0]))

        elapsed_time = 1000 * (time.time() - start_time)
        logger.info("{} {} {} {} elapsed_time [ms]={:.5f} job_id={} file_name={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", elapsed_time, job_id, file_names[0]))
        return FileResponse(
            os.path.join(PredictServerConfig.cache_dir, job_id, "out", file_names[0])
        )

    @app.post("/clear_cache")
    def clear_cache():
        shutil.rmtree(PredictServerConfig.cache_dir)
        if not os.path.isdir(PredictServerConfig.cache_dir):
            os.mkdir(PredictServerConfig.cache_dir)
        return

    @app.post("/clear_log")
    def clear_log():
        if( os.path.exists(os.path.join("log", 'app.log')) ):
            os.remove(os.path.join("log", 'app.log'))
        logger_fh = logging.FileHandler(os.path.join("log", 'app.log'))
        logger.addHandler(logger_fh)
        logger.info("{} {} start predict-api server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO"))
        return

    def upload_file(job_id: str, file: UploadFile = File(...)):
        start_time = time.time()
        logger.info("{} {} {} {} file_name={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", file.filename))
        try:
            with open(os.path.join(PredictServerConfig.cache_dir, job_id, "in", file.filename),'wb+') as buffer:
                shutil.copyfileobj(file.file, buffer)
            responce = {
                "status": "ok",
                "file_name": file.filename,
                "file_path": os.path.join(PredictServerConfig.cache_dir, job_id, "in", file.filename),
            }
        except Exception as e:
            responce = {
                "status": "ng",
                "file_name": None,
                "file_path": None,
            }
        finally:
            file.file.close()

        elapsed_time = 1000 * (time.time() - start_time)
        logger.info("{} {} {} {} elapsed_time [ms]={:.5f} file_name={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", elapsed_time, file.filename))
        return responce

    @app.post("/predict")
    def predict(
        job_id: str,
        file: UploadFile = File(...),
    ):
        logger.info('[{}] time {} | job_id={}, file_name={} のリクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id, file.filename))
        if not os.path.isdir( os.path.join(PredictServerConfig.cache_dir,job_id) ):
            os.mkdir( os.path.join(PredictServerConfig.cache_dir,job_id) )
        if not os.path.isdir( os.path.join(PredictServerConfig.cache_dir, job_id, "in") ):
            os.mkdir( os.path.join(PredictServerConfig.cache_dir, job_id, "in") )
        if not os.path.isdir( os.path.join(PredictServerConfig.cache_dir, job_id, "out") ):
            os.mkdir( os.path.join(PredictServerConfig.cache_dir, job_id, "out") )

        uploaded_file = upload_file(job_id=job_id, file=file)

        # ffmpeg を用いた動画の無音化処理 / ffmpeg -i input.mp4 -an output.mp4
        subprocess.call([
            'ffmpeg', '-y',
            '-i', uploaded_file["file_path"],
            '-vf', 'scale={}:{}'.format(PredictServerConfig.video_height, PredictServerConfig.video_width),
            os.path.join(PredictServerConfig.cache_dir, job_id, "out", uploaded_file["file_path"].split("/")[-1])
        ])

        # 非同期処理の効果を明確化するためにあえて sleep 処理
        time.sleep(1)

        # レスポンスデータ設定
        print('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
        logger.info('[{}] time {} | job_id={}, file_name={} リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id, file.filename))
        return {
            "status": "ok",
            "job_id": job_id,
        }
    ```

    ポイントは、以下の通り

    > 推論サーバーは同期処理での API なので、`http://${HOST}:${PORT}/predict` のエンドポイントで `FileResponse()` オブジェクトを return してもよかったが、この場合 `curl -X POST` コマンドでリクエストする場合に、｛`job_id` のパスパラメーター・curl コマンドの `--form` で指定するアップロードファイル・curl コマンドの `--output` で指定する出力ファイル｝を同時に指定できなかった。同様に、`requests.post()` でリクエストする場合も、｛`job_id` のパスパラメーター・curl コマンドの `--form` で指定するアップロードファイル・curl コマンドの `--output` で指定する出力ファイル｝を同時に指定できなかった。そのため、`FileResponse()` オブジェクトは、別のエンドポイント `http://${HOST}:${PORT}/get_job/${JOB_ID}` で取得するようにしている。


    > [ToDo] ｛`job_id` のパスパラメーター・curl コマンドの `--form` で指定するアップロードファイル・curl コマンドの `--output` で指定する出力ファイル｝を同時に指定する `curl` コマンド、または `requests.post()` の方法を見つける


1. docker-compose で API を構成する<br>
    プロキシサーバー・バッチサーバー・推論サーバーを docker-compose で構築する。
    ```python
    ```    

1. リクエスト処理のコードを作成する<br>
    `requests` モジュールを用いて、例えば以下のようなリクエスト処理のコードを作成する。
    
    ```python
    ```

    ポイントは、以下の通り

    > xxx

1. API を起動する<br>
    ```sh
    $ docker-compose -f docker-compose.yml stop
    $ docker-compose -f docker-compose.yml up -d
    ```

1. リクエスト処理する<br>
    上記作成したリクエスト処理のコードを用いてリクエスト処理する場合は、以下のコマンドを実行する
    ```sh
    HOST=0.0.0.0
    PORT=5000
    N_POLLINGS=100

    IN_VIDEO_DIR=in_video
    OUT_VIDEO_DIR=out_video
    rm -rf ${OUT_VIDEO_DIR}

    # ヘルスチェック
    curl http://${HOST}:${PORT}/health

    # キャッシュクリア
    curl -X POST http://${HOST}:${PORT}/clear_cache

    # log クリア
    curl -X POST http://${HOST}:${PORT}/clear_log

    # リクエスト処理
    python request.py --host ${HOST} --port ${PORT} --in_video_dir ${IN_VIDEO_DIR} --out_video_dir ${OUT_VIDEO_DIR} --n_pollings ${N_POLLINGS}
    ```
