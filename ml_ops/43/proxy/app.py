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
sys.path.append(os.path.join(os.getcwd(), '../config'))
from config import PredictServerSyncConfig, PredictServerAsyncConfig

sys.path.append(os.path.join(os.getcwd(), '../utils'))
from utils import conv_base64_to_pillow, conv_pillow_to_base64
from logger import log_base_decorator, log_decorator

sys.path.append(os.path.join(os.getcwd(), '../redis'))
from redis_client import redis_client
from redis_utils import set_image_pillow_redis, set_image_base64_redis, get_image_pillow_redis, get_image_base64_redis

# logger
if( os.path.exists(__name__ + '.log') ):
    os.remove(__name__ + '.log')
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler(__name__ + '.log')
logger.addHandler(logger_fh)

#------------------------
# Fast API
#------------------------
app = FastAPI()

class ImageData(BaseModel):
    """
    画像データのリクエストボディ
    """
    image: Any

class SetDataRedisJob(BaseModel):
    """
    非同期処理での Job を定義したジョブクラス
    """
    job_id: str
    img_base64: Any
    def __call__(self):
        jobs[self.job_id] = self
        try:
            # Redis キューの先頭に job_id を追加
            redis_client.lpush("job_id", self.job_id)
            redis_client.lpush(self.job_id + "_job_status", "RUNNING")
            print('[{}] time {} | Job {} を登録しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))
            logger.info('[{}] time {} | Job {} を登録しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))

            # 画像を追加
            set_image_base64_redis(redis_client=redis_client, key_name=self.job_id + "_image_in", img_base64=self.img_base64)
        except Exception:
            print('[{}] time {} | Job {} の登録に失敗しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))
            logger.info('[{}] time {} | Job {} の登録に失敗しました'.format(self.__class__.__name__, f"{datetime.now():%H:%M:%S}", self.job_id))

        return

jobs : Dict[str, SetDataRedisJob] = {}

#------------------------
# エンドポイント
#------------------------
@app.get("/")
def root():
    return 'Hello Proxy Server!\n'

@log_base_decorator(logger=logger)
def _health():
    try:
        health_predict_server_sync = requests.get("http://" + PredictServerSyncConfig.host + ":" + PredictServerSyncConfig.port + "/health").json()
    except Exception as e:
        health_predict_server_sync = {"health": "ng"}

    try:
        health_predict_server_async = requests.get("http://" + PredictServerAsyncConfig.host + ":" + PredictServerAsyncConfig.port + "/health").json()
    except Exception as e:
        health_predict_server_async = {"health": "ng"}

    return {
        "proxy_server" : {"health": "ok"},
        "predict_server_sync" : health_predict_server_sync,
        "predict_server_async" : health_predict_server_async,
    }

@app.get("/health")
def health():
    return _health()

@app.get("/metadata")
def metadata():    
    return

@app.get("/get_job/{job_id}")
def get_job(
    job_id: str,  # パスパラメーター
):
    job_status = redis_client.rpop(job_id + "_job_status")
    redis_client.lpush(job_id + "_job_status", job_status)

    if( job_status == "SUCCEED" ):
        status = "ok"
    else:
        status = "ng"

    try:
        img_in_base64 = get_image_base64_redis( redis_client=redis_client, key_name=job_id + "_image_in" )
    except Exception:
        img_in_base64 = None
        status = "ng"
    try:
        img_out_base64 = get_image_base64_redis( redis_client=redis_client, key_name=job_id + "_image_out" )
    except Exception:
        img_out_base64 = None
        status = "ng"

    return {
        "job_id" : jobs[job_id].job_id,
        "job_status" : job_status,
        "status": status,
        "img_in_base64" : img_in_base64,
        "img_out_base64" : img_out_base64,
    }

@app.post("/predict")
def predict(
    img_data: ImageData,                # リクエストボディ
    background_tasks: BackgroundTasks,  # BackgroundTasks
):
    start_time = time.time()

    # job_id を自動生成
    job_id = str(uuid.uuid4())[:6]
    logger.info("{} {} {} {} job_id={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", job_id))

    # 同期推論サーバーへのリクエスト処理 / 同期的にレスポンスされる
    try:
        api_responce = requests.post("http://" + PredictServerSyncConfig.host + ":" + PredictServerSyncConfig.port + "/predict", json={'image': img_data.image}, params={"job_id": job_id} )
        api_responce = api_responce.json()
        logger.info('[{}] time {} | api_responce["status"] {}'.format(__name__, f"{datetime.now():%H:%M:%S}", api_responce["status"]))
    except Exception as e:
        print( "Exception : ", e )
        logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))
        api_responce = {
            "job_id" : job_id,
            "status" : "ng",
            "img_none_bg_base64" : None,
        }

    # 非同期推論サーバーへのリクエスト処理
    # バックグラウンドで Redis に key:job_id, value:base64画像 のキューデータ追加を追加し、バッチサーバーのポーリング処理して非同期レスポンスされる
    task = SetDataRedisJob(job_id=job_id, img_base64=img_data.image)
    background_tasks.add_task(task)

    elapsed_time = 1000 * (time.time() - start_time)
    logger.info("{} {} {} {} job_id={}, elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", job_id, elapsed_time))
    return api_responce
