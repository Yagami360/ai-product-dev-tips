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

@app.get("/get/{job_id}")
async def get_job(
    job_id: str,  # パスパラメーター
):
    """
    status = "ok"
    try:
        out_file_path = redis_client.get(job_id + "_out_file_path").decode()
        logger.info('[{}] time {} | job_id={}, out_file_path="{}" を get しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id, out_file_path))
    except Exception:
        status = "ng"    
        return {
            "status": status,
            "job_id" : jobs[job_id].job_id,
            "job_status" : jobs[job_id].job_status,
            "out_file_path" : "",
            "out_file":"",
        }

    return {
        "status": status,
        "job_id" : jobs[job_id].job_id,
        "job_status" : jobs[job_id].job_status,
        "out_file_path" : out_file_path,
        "out_file": FileResponse(out_file_path),
    }
    """
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
