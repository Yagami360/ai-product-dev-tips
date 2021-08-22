import os
import asyncio
from datetime import datetime
import time
import logging
import uuid
#import ssl

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

from api_utils import graph_cut

import sys
sys.path.append(os.path.join(os.getcwd(), '..'))
from config import PredictServerConfig
from utils.utils import conv_base64_to_pillow, conv_pillow_to_base64
from utils.logger import log_base_decorator, log_decorator

# logger
if not os.path.isdir("log"):
    os.mkdir("log")
"""
if( os.path.exists(os.path.join("log", 'app.log')) ):
    os.remove(os.path.join("log", 'app.log'))
"""
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler(  os.path.join("log", __name__+'.log') )
logger.addHandler(logger_fh)

app = FastAPI()
print('[{}] time {} | APIサーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
logger.info('[{}] time {} | APIサーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

class ImageData(BaseModel):
    """
    画像データのリクエストボディ
    """
    image: Any

@app.get("/")
def root():
    return 'Hello API Server!\n'

@log_base_decorator(logger=logger)
def _health():
    return {"health": "ok"}

@app.get("/health")
def health():
    return _health()

@app.get("/metadata")
def metadata():
    return

@app.post("/predict")
def predict(
    img_data: ImageData,        # リクエストボディ    
):
    job_id = str(uuid.uuid4())[:6]

    start_time = time.time()
    #logger.info("{} {} {} {} ".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START"))
    logger.info("{} {} {} {} job_id={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", job_id))
    
    # base64 -> Pillow への変換
    img_data.image = conv_base64_to_pillow(img_data.image)

    # OpenCV を用いて背景除去
    _, img_none_bg_pillow = graph_cut(img_data.image, binary_threshold=PredictServerConfig.binary_threshold)

    # Pillow -> base64 への変換
    img_none_bg_base64 = conv_pillow_to_base64(img_none_bg_pillow)

    # 非同期処理の効果を明確化するためにあえて sleep 処理
    #time.sleep(1)

    elapsed_time = 1000 * (time.time() - start_time)
    #logger.info("{} {} {} {} elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", elapsed_time))
    logger.info("{} {} {} {} job_id={}, elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", job_id, elapsed_time))

    # レスポンスデータ設定
    return {
        "status": "ok",
        "img_none_bg_base64" : img_none_bg_base64,
    }
