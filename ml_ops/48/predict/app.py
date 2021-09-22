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

"""
@app.get("/get/{job_id}")
def get_job(
    job_id: str,  # パスパラメーター
):
    return FileResponse(
        os.path.join(PredictServerConfig.cache_dir, job_id, "" )
    )
"""

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
    return

def upload_file(job_id: str, file: UploadFile = File(...)):
    start_time = time.time()
    logger.info("{} {} {} {} file_name={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", file.filename))
    try:
        with open(os.path.join(PredictServerConfig.cache_dir, job_id, file.filename),'wb+') as buffer:
            shutil.copyfileobj(file.file, buffer)
        responce = {
            "status": "ok",
            "file_name": file.filename,
            "file_path": os.path.join(PredictServerConfig.cache_dir, job_id, file.filename),
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

    uploaded_file = upload_file(job_id=job_id, file=file)

    # ffmpeg を用いた動画の無音化処理 / ffmpeg -i input.mp4 -an output.mp4
    subprocess.call([
        'ffmpeg', '-y',
        '-i', uploaded_file["file_path"],
        '-vf', 'scale={}:-1'.format(PredictServerConfig.video_height),
        uploaded_file["file_path"].split(".mp4")[0] + "_out.mp4",
    ])

    # 非同期処理の効果を明確化するためにあえて sleep 処理
    time.sleep(1)

    # レスポンスデータ設定
    print('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    logger.info('[{}] time {} | job_id={}, file_name={} リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id, file.filename))
    #return {"status": "ok",}
    return FileResponse(uploaded_file["file_path"].split(".mp4")[0] + "_out.mp4")
