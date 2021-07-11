import os
import logging
from datetime import datetime
import time
import asyncio
import time
import requests
import httpx
import uuid
from PIL import Image

from fastapi import FastAPI
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
        health_predict_server1 = requests.get(ProxyServerConfig.predict_server1_url + "/health").json()
    except Exception as e:
        health_predict_server1 = {"health": "ng"}

    try:
        health_predict_server2 = requests.get(ProxyServerConfig.predict_server2_url + "/health").json()
    except Exception as e:
        health_predict_server2 = {"health": "ng"}

    try:
        health_predict_server3 = requests.get(ProxyServerConfig.predict_server3_url + "/health").json()
    except Exception as e:
        health_predict_server3 = {"health": "ng"}

    return {
        "proxy_server" : {"health": "ok"},
        "predict_server1" : health_predict_server1,
        "predict_server2" : health_predict_server2,
        "predict_server3" : health_predict_server3,
    }

@app.get("/health")
def health():
    return _health()

@app.get("/metadata")
def metadata():    
    return

@app.post("/predict")
async def predict(
    img_data: ImageData,                # リクエストボディ
):
    start_time = time.time()

    # job_id を自動生成
    job_id = str(uuid.uuid4())[:6]
    logger.info("{} {} {} {} job_id={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", job_id))

    # base64 
    img_base64 = img_data.image

    # 複数の Web-API に並列リクエスト
    async with httpx.AsyncClient() as client:
        # リクエスト処理を行うメソッド
        async def request(client, end_point, job_id, img_base64):
            response = await client.post(f"{end_point}", json={"image": img_base64}, params={"job_id": job_id})
            return response

        # asyncio.gather() で並列処理
        # 実行される順序は不定になるが、処理した結果については渡した順に返される
        # await 構文を付与することで、全ての並列処理が完了するまで wait するようにする
        tasks = [
            request(client, ProxyServerConfig.predict_server1_url + "/predict", job_id, img_base64),
            request(client, ProxyServerConfig.predict_server2_url + "/predict", job_id, img_base64),
            request(client, ProxyServerConfig.predict_server3_url + "/predict", job_id, img_base64),
        ]
        responses = await asyncio.gather(*tasks)

        results = []
        for response in responses:
            results.append(response.json())

    elapsed_time = 1000 * (time.time() - start_time)
    logger.info("{} {} {} {} job_id={}, elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", job_id, elapsed_time))
    return results
