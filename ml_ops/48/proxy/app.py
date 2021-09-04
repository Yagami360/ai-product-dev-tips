import os
import logging
from datetime import datetime
import time
import asyncio
import uuid
import shutil

from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
from fastapi import BackgroundTasks
from pydantic import BaseModel
from typing import Any, Dict

import sys
sys.path.append(os.path.join(os.getcwd(), '../config'))
from config import ProxyServerConfig

if not os.path.isdir(ProxyServerConfig.tmp_dir):
    os.mkdir(ProxyServerConfig.tmp_dir)

# logger
if( os.path.exists(__name__ + '.log') ):
    os.remove(__name__ + '.log')
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler(__name__ + '.log')
logger.addHandler(logger_fh)

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
            if not os.path.isdir( os.path.join(ProxyServerConfig.tmp_dir,self.job_id) ):
                os.mkdir( os.path.join(ProxyServerConfig.tmp_dir,self.job_id) )

            # job_id に対応したディレクトリ以下に動画データを保存
            with open(os.path.join(ProxyServerConfig.tmp_dir,self.job_id,self.file.filename),'wb+') as buffer:
                shutil.copyfileobj(self.file.file, buffer)

            self.file_name = self.file.filename
            self.file_path = os.path.join(ProxyServerConfig.tmp_dir,self.job_id,self.file.filename)
            logger.info('[{}] time {} | job_id={} の動画データを保存しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))

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

"""
@app.get("/get/{job_id}")
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
"""

"""
#@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    start_time = time.time()
    logger.info("{} {} {} {} file_name={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", file.filename))
    try:
        with open(os.path.join(ProxyServerConfig.tmp_dir, file.filename),'wb+') as buffer:
            shutil.copyfileobj(file.file, buffer)
        responce = {
            "status": "ok",
            "file_name": file.filename,
            "file_path": os.path.join(ProxyServerConfig.tmp_dir,file.filename),
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

"""

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,  # BackgroundTasks
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
