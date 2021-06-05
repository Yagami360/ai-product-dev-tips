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
    job_status: str = "RUNNING"
    is_cancelled: bool = False

    def __call__(self):
        jobs[self.job_id] = self
        self.job_status = "RUNNING"
        print('[Job] time {} | step {} | Job {} が開始されました'.format(f"{datetime.now():%H:%M:%S}", 0, self.job_id))
        logger.info('[Job] time {} | step {} | Job {} が開始されました'.format(f"{datetime.now():%H:%M:%S}", 0, self.job_id))

        """
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
        """

        #del jobs[self.job_id]
        self.job_status = "FINISHED"
        print('[Job] time {} | step {} | Job {} が終了しました'.format(f"{datetime.now():%H:%M:%S}", step, self.job_id))
        logger.info('[Job] time {} | step {} | Job {} が終了しました'.format(f"{datetime.now():%H:%M:%S}", step, self.job_id))
        return

jobs : Dict[int, Job] = {}

@app.get("/")
async def root():
    return 'Hello Proxy Server!\n'

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
    background_tasks: BackgroundTasks,  # BackgroundTasks
):
    # ジョブクラスのオブジェクト作成
    task = Job(job_id=job_id)

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
