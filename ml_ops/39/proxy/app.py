import os
import logging
from datetime import datetime
import time
import asyncio
import time
import requests
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

sys.path.append(os.path.join(os.getcwd(), '../redis'))
from redis_client import redis_client
from redis_utils import set_image_pillow_redis, set_image_base64_redis, get_image_pillow_redis, get_image_base64_redis

app = FastAPI()

# logger
"""
if( os.path.exists(__name__ + '.log') ):
    os.remove(__name__ + '.log')
"""
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler(__name__ + '.log')
logger.addHandler(logger_fh)


class ImageData(BaseModel):
    """
    画像データのリクエストボディ
    """
    file_path: str
    img_base64: Any

class CacheDataRedisJob(BaseModel):
    file_name: str
    img_base64: Any

    def __call__(self):
        jobs[self.file_name] = self
        try:
            # Redis キューの先頭に file_name:img_base64 のキーデータを追加
            redis_client.lpush("file_name", self.file_name)
            print('[{}] time {} | FileName {} を登録しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.file_name))
            logger.info('[{}] time {} | FileName {} を登録しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.file_name))

            # 画像を追加
            set_image_base64_redis(redis_client=redis_client, key_name=self.file_name, img_base64=self.img_base64)

        except Exception:
            print('[{}] time {} | FileName {} の登録に失敗しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.file_name))
            logger.info('[{}] time {} | FileName {} の登録に失敗しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.file_name))

        return

jobs : Dict[str, CacheDataRedisJob] = {}

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
    background_tasks: BackgroundTasks,  # BackgroundTasks
):
    start_time = time.time()

    # job_id を自動生成
    job_id = str(uuid.uuid4())[:6]
    logger.info("{} {} {} {} job_id={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", job_id))

    # キューに推論済みのキャッシュデータが存在するか確認
    cache_img_base64 = get_image_base64_redis(redis_client, key_name=img_data.file_path)

    # キューに推論済みのデータが存在しない場合
    if(cache_img_base64 == None):
        logger.info(f"registering cache: {img_data.file_path}")

        # Web-API に推論リクエスト
        try:
            api_responce = requests.post( ProxyServerConfig.predict_server_url + "/predict", json={'image': img_data.img_base64}, params={"job_id": job_id} )
            api_responce = api_responce.json()

            # 推論データをキャッシュに保存
            task = CacheDataRedisJob(file_name=img_data.file_path, img_base64=api_responce["img_none_bg_base64"])      # ジョブクラスのオブジェクト作成
            background_tasks.add_task(task)                                                                            # BackgroundTasks にジョブを追加

            responce = {
                "status" : "ok",
                "img_none_bg_base64" : api_responce["img_none_bg_base64"],
            }

        except Exception as e:
            print( "Exception : ", e )
            logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))
            responce = {
                "status" : "ng",
                "img_none_bg_base64" : None,
            }
    else:
        logger.info(f"cache hit: {img_data.file_path}")
        responce = {
            "status" : "ok",
            "img_none_bg_base64" : cache_img_base64,
        }

    elapsed_time = 1000 * (time.time() - start_time)
    logger.info("{} {} {} {} job_id={}, elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", job_id, elapsed_time))
    return responce
