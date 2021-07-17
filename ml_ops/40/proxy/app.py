import os
import logging
from datetime import datetime
import time
import time
import requests
import uuid

from fastapi import FastAPI, params
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
        health_predict_server = requests.get(ProxyServerConfig.predict_server_url + "/health").json()
    except Exception as e:
        health_predict_server = {"health": "ng"}

    return {
        "proxy_server" : {"health": "ok"},
        "predict_server" : health_predict_server,
    }

@app.get("/health")
def health():
    return _health()

@app.get("/metadata")
def metadata():    
    return

@app.post("/predict")
def predict(
    img_data: ImageData,                # リクエストボディ
):
    start_time = time.time()

    # job_id を自動生成
    job_id = str(uuid.uuid4())[:6]
    logger.info("{} {} {} {} job_id={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", job_id))

    # 推論サーバーにリクエスト処理
    try:
        api_responce = requests.post( ProxyServerConfig.predict_server_url + "/predict", json={'image': img_data.image}, params={"job_id": job_id} )
        api_responce = api_responce.json()
        logger.info('[{}] time {} | api_responce["status"] {}'.format(__name__, f"{datetime.now():%H:%M:%S}", api_responce["status"]))
    except Exception as e:
        print( "Exception : ", e )
        logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))
        api_responce = {
            "status" : "ng",
            "img_none_bg_base64" : None,
        }

    elapsed_time = 1000 * (time.time() - start_time)
    logger.info("{} {} {} {} job_id={}, elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", job_id, elapsed_time))
    return api_responce
