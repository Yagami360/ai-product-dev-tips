import os
import logging
from datetime import datetime
from time import sleep
import asyncio
import redis
import uuid

from fastapi import FastAPI
from fastapi import BackgroundTasks
from pydantic import BaseModel
from typing import Dict

import sys
sys.path.append(os.path.join(os.getcwd(), '../redis'))
from redis_client import redis_client

app = FastAPI()

# logger
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler( __name__ + '.log')
logger.addHandler(logger_fh)

class SetDataRedisJob(BaseModel):
    """
    非同期処理での Job を定義したジョブクラス
    """
    job_id: str
    job_status: str = "RUNNING"

    def __call__(self):
        jobs[self.job_id] = self
        self.job_status = "RUNNING"
        try:
            # Redis キューの先頭に値を追加
            redis_client.lpush("job_id", self.job_id)
            print('[{}] time {} | Job {} を登録しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))
            logger.info('[{}] time {} | Job {} を登録しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))
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
    return {"health": "ok"}

@app.get("/metadata")
async def metadata():    
    return {
        "jobs" : jobs,
    }

@app.get("/get_job/{job_id}")
async def get_job(
    job_id: str,  # パスパラメーター
):
    try:
        data = redis_client.get(job_id)
        return data
    except Exception:
        return {"message", "ジョブ {} は実行されていません".format(job_id)}

@app.post("/start_job/")
async def start_job(
    background_tasks: BackgroundTasks,  # BackgroundTasks
):
    # job_id を自動生成
    job_id = str(uuid.uuid4())[:6]

    # ジョブクラスのオブジェクト作成
    task = SetDataRedisJob(job_id=job_id)

    # BackgroundTasks にジョブを追加
    background_tasks.add_task(task)

    return job_id
