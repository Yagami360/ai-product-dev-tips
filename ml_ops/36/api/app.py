# coding=utf-8
import os
import sys
import argparse
import time
from datetime import datetime
import logging
import uuid
from typing import Any, Dict

from fastapi import FastAPI
from fastapi import BackgroundTasks, HTTPException
from pydantic import BaseModel

# 自作モジュール
from utils.logger import log_base_decorator, log_json_base_decorator
from utils.img_utils import conv_base64_to_pillow, conv_pillow_to_base64
from config import APIConfig

sys.path.append(os.path.join(os.getcwd(), '../'))
from mysql_utils.setting import global_session, get_context_session
from mysql_utils import crud
from mysql_utils import converter

#--------------------------
# logger
#--------------------------
if not os.path.isdir("log"):
    os.mkdir("log")
if( os.path.exists(os.path.join("log", __name__ + '.log')) ):
    os.remove(os.path.join("log", __name__ + '.log'))

logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler(os.path.join("log", __name__ + '.log'))
logger.addHandler(logger_fh)
logger.info("{} {} {} start api server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", __name__))
"""
logger.info({
    "time_stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "func": __name__,
    "info": "start api server",
})
"""

#--------------------------
# FastAPI
#--------------------------
app = FastAPI()

class ImageData(BaseModel):
    """
    画像データのリクエストボディ
    """
    image: Any

#--------------------------
# MySQL (SQLAlchemy)
#--------------------------
crud.init()

#======================================
# GET method
#======================================
@app.get("/")
def root():
    return 'Hello Flask-API Server!\n'

@log_base_decorator(logger=logger)
#@log_json_base_decorator(logger=logger)
def _health():
    return {"health": "ok"}

@app.get("/health")
def health():
    return _health()

@log_base_decorator(logger=logger)
#@log_json_base_decorator(logger=logger)
def _metadata():
    return {
        "APIConfig" : {
            "threshold": APIConfig.threshold,
        },
    }

@app.get("/metadata")
def metadata():
    return _metadata()

@app.get("/log_all")
def get_log_all():
    with get_context_session() as session:
        data = crud.select_all(session)
    return converter.convert_table_to_json(data)

@app.get("/log_first")
def get_log_first():
    with get_context_session() as session:
        data = crud.select_first(session)
    return converter.convert_table_to_json(data)

#======================================
# POST method
#======================================
@log_base_decorator(logger=logger)
#@log_json_base_decorator(logger=logger)
def _predict(
    job_id: str,
    img_data: ImageData,
):
    # base64 -> Pillow への変換
    img_pillow = conv_base64_to_pillow(img_data.image)

    # ２値化
    img_gray_pillow = img_pillow.convert("L")
    img_gray_pillow.point(lambda x: 0 if x < APIConfig.threshold else x)

    # Pillow -> base64 への変換
    img_base64 = conv_pillow_to_base64(img_gray_pillow)

    return {
        "job_id": job_id,
        "status": "ok",
        "img_base64" : img_base64,
    }

@app.post("/predict/")
def predict(
    img_data: ImageData,                # リクエストボディ 
    background_tasks: BackgroundTasks,  # BackgroundTasks
):
    start_time = time.time()
    job_id = str(uuid.uuid4())[:6]
    predict_data = _predict(job_id=job_id, img_data=img_data)
    elapsed_time = 1000 * (time.time() - start_time)

    # バックグラウンドで MySQL にログデータを追加
    background_tasks.add_task(
        insert_mysql,                                               # バックグラウンド処理を行うメソッド名
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # メソッドの引数
        func_name = sys._getframe().f_code.co_name,                 # ↑
        elapsed_time = elapsed_time,                                # ↑
        job_id = job_id,                                            # ↑
    )

    return predict_data


def insert_mysql(time_stamp, func_name, elapsed_time, job_id):
    """
    MySQL にログデータ追加
    """
    with get_context_session() as session:
        log = {
            "time_stamp": time_stamp, 
            "func_name": func_name,
            "elapsed_time": elapsed_time,                       
            "job_id" : job_id,
        }
        crud.insert(session=session, id=job_id, data=log)

    return