import os
import asyncio
from datetime import datetime
from time import sleep
import logging
from PIL import Image

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

import sentry_sdk   # Sentry の Pyhton SDK

import sys
from utils.utils import conv_base64_to_pillow, conv_pillow_to_base64

# logger
if( os.path.exists(__name__ + '.log') ):
    os.remove(__name__ + '.log')
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler( __name__ + '.log')
logger.addHandler(logger_fh)

# sentry sdk 初期化
sentry_sdk.init(
    "https://c3773729429b4e1a8b2c7d35424178f4@o1171856.ingest.sentry.io/6266790",   # DNS の値

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

#------------------------------
# FastAPI の初期化
#------------------------------
app = FastAPI()
print('[{}] time {} | 推論サーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
logger.info('[{}] time {} | 推論サーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

class ImageData(BaseModel):
    """
    画像データのリクエストボディ
    """
    image: Any
    image_height: Any
    image_width: Any

#------------------------------
# GET Method
#------------------------------
@app.get("/")
def root():
    return 'Hello API Server!\n'

@app.get("/health")
def health():
    return {"health": "ok"}

@app.get("/metadata")
def metadata():
    return

#------------------------------
# POST Method
#------------------------------
@app.post("/predict")
def predict(
    img_data: ImageData,        # リクエストボディ    
):
    print('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    logger.info('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

    if(img_data.image_height >= 1024 or img_data.image_width >= 1024 ):
        # logger.error() で出力した ERROR レベルのログデータは Sentry で検出される 
        logger.error('[{}] time {} | image_height={}, image_width={}| 画像サイズの値が大き過ぎます'.format(__name__, f"{datetime.now():%H:%M:%S}", img_data.image_height, img_data.image_width))

        # 例外も Sentry で検出される
        raise Exception('too high image size exception.')
        """
        return {
            "status": "ng",
            "img_resized_base64" : None,
        }
        """
        
    # base64 -> Pillow への変換
    img_data.image = conv_base64_to_pillow(img_data.image)

    # resize
    img_resized_pillow = img_data.image.resize((img_data.image_width, img_data.image_height), Image.LANCZOS)

    # Pillow -> base64 への変換
    img_resized_base64 = conv_pillow_to_base64(img_resized_pillow)

    # レスポンスデータ設定
    print('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    logger.info('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

    return {
        "status": "ok",
        "img_resized_base64" : img_resized_base64,
    }