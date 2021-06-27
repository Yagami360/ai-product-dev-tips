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
from config import APIConfig
sys.path.append(os.path.join(os.getcwd(), '../'))
from utils.logger import log_base_decorator, log_json_base_decorator
from utils.img_utils import conv_base64_to_pillow, conv_pillow_to_base64

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
def _health():
    return {"health": "ok"}

@app.get("/health")
def health():
    return _health()

@log_base_decorator(logger=logger)
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
def _predict(
    job_id: str,
    img_data: ImageData,
):
    # MySQL にジョブデータ｛ジョブID・入力画像｝を保存する
    with get_context_session() as session:
        crud.insert(session=session, job_id=job_id, image_in=img_data.image)

    return {
        "job_id": job_id,
        "status": "ok",
    }

@app.post("/predict/")
def predict(
    img_data: ImageData,                # リクエストボディ 
):
    job_id = str(uuid.uuid4())[:6]
    predict_data = _predict(job_id=job_id, img_data=img_data)
    return predict_data

