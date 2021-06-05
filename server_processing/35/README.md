# FastAPI での非同期処理（FastAPI + uvicorn + gunicorn + docker での構成）

FastAPI を使用すれば、Flask では困難であった非同期処理を手軽に行うことができる。<br>

この方法を用いて例えば Web-API を非同期処理にした場合は、API での処理が終わるまでクライアント側で別の処理を行えるようになるメリットがある。
但し、クライアント側で処理が完了したかのポーリング処理は必要になる

- FastAPI で非同期処理を行うコード例
    ```python
    import asyncio
    from datetime import datetime
    from time import sleep
    import logging

    from fastapi import FastAPI
    from fastapi import BackgroundTasks
    from pydantic import BaseModel
    from typing import Dict

    app = FastAPI()

    logger = logging.getLogger(__name__)
    logger.setLevel(10)
    logger_fh = logging.FileHandler( __name__ + '.log')
    logger.addHandler(logger_fh)

    class Job(BaseModel):
        """
        非同期処理での Job を定義したジョブクラス
        """
        job_id: int
        n_steps: int = 10
        job_status: str = "RUNNING"
        is_cancelled: bool = False

        def __call__(self):
            jobs[self.job_id] = self
            self.job_status = "RUNNING"
            print('[Job] time {} | step {} | Job {} が開始されました'.format(f"{datetime.now():%H:%M:%S}", 0, self.job_id))
            logger.info('[Job] time {} | step {} | Job {} が開始されました'.format(f"{datetime.now():%H:%M:%S}", 0, self.job_id))

            for step in range(self.n_steps):
                # ジョブの処理
                sleep(1)
                print('[Job] time {} | step {} | Job {} を実行中です'.format(f"{datetime.now():%H:%M:%S}", step, self.job_id))
                logger.info('[Job] time {} | step {} | Job {} を実行中です'.format(f"{datetime.now():%H:%M:%S}", step, self.job_id))
                if self.is_cancelled:
                    del jobs[self.job_id]
                    self.job_status = "CANCELLED"
                    print('[Job] time {} | step {} | Job {} が中断されました'.format(f"{datetime.now():%H:%M:%S}", step, self.job_id))
                    logger.info('[Job] time {} | step {} | Job {} が中断されました'.format(f"{datetime.now():%H:%M:%S}", step, self.job_id))
                    break

            #del jobs[self.job_id]
            self.job_status = "FINISHED"
            print('[Job] time {} | step {} | Job {} が終了しました'.format(f"{datetime.now():%H:%M:%S}", step, self.job_id))
            logger.info('[Job] time {} | step {} | Job {} が終了しました'.format(f"{datetime.now():%H:%M:%S}", step, self.job_id))
            return

    jobs : Dict[int, Job] = {}

    @app.get("/")
    async def root():
        return 'Hello Flask-API Server!\n'

    @app.get("/health")
    async def health():
        return {"health": "ok"}

    @app.get("/metadata")
    async def metadata():
        return jobs

    @app.get("/get_job/{job_id}")
    async def get_job(
        job_id: int,  # パスパラメーター
    ):
        if job_id in jobs:
            return jobs[job_id]
        else:
            return {"message", "ジョブID : {} のジョブは実行されていません".format(job_id)}

    @app.post("/start_job/{job_id}")
    async def start_job(
        job_id: int,                        # パスパラメーター
        n_steps: int,                       # クエリパラメーター
        background_tasks: BackgroundTasks,  # BackgroundTasks
    ):
        # ジョブクラスのオブジェクト作成
        task = Job(job_id=job_id, n_steps=n_steps)

        # BackgroundTasks にジョブを追加
        background_tasks.add_task(task)

        return {"message", "ジョブID : {} のジョブを開始しました".format(job_id)}

    @app.post("/stop_job/{job_id}")
    async def stop_job(
        job_id: int,                        # パスパラメーター
        background_tasks: BackgroundTasks,  # BackgroundTasks
    ):
        # job のリストから作成済みのジョブオブジェクトを取得
        # dict の get() を使用することで、キーが存在しない場合にエラーを発生させずに任意の値（デフォルト値）を取得する
        task = jobs.get(job_id)
        if task is None:
            return {"message", "ジョブID : {} のジョブは実行されていません".format(job_id)}
                    
        # ジョブの中断フラグを ON にする
        task.is_cancelled = True
        return {"message", "ジョブID : {} のジョブを中断しました".format(job_id)}
    ```

    ```sh
    # ジョブ開始
    curl -X POST http://${HOST}:${PORT}/start_job/0?n_steps=100
    curl -X POST http://${HOST}:${PORT}/start_job/1?n_steps=10
    curl -X POST http://${HOST}:${PORT}/start_job/2?n_steps=20
    ```
    ```sh
    # ジョブ中断
    curl -X POST http://${HOST}:${PORT}/stop_job/0
    ```
    ```sh
    # ジョブの確認
    curl -X GET http://${HOST}:${PORT}/get_job/0
    curl -X GET http://${HOST}:${PORT}/get_job/1 
    curl -X GET http://${HOST}:${PORT}/get_job/2       
    ```

ポイントは、以下の通り

- python3 の `asyncio` モジュールの機能である `async def` を使用して GET, POST などの関数を定義する。ここで、`async def` 単体では、非同期処理（マルチスレッド処理）にはならないことに注意。
- 非同期処理（バックグラウンド処理）したい Job の内容を `pydantic.BaseModel` 継承クラスとして定義する
- FastAPI の `BackgroundTask` モジュールの `add_task()` メソッドを使用して、作成した Job をバックグラウンド処理として追加する

## ■ 参考サイト
- https://qiita.com/juri-t/items/91e561509aa7ca6e7d38