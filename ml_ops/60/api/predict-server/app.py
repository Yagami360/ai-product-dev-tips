import os
import asyncio
from datetime import datetime
from time import sleep
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

from api_utils import graph_cut

import sys
sys.path.append(os.path.join(os.getcwd(), '../utils'))
from utils import conv_base64_to_pillow, conv_pillow_to_base64

# logger
if not os.path.isdir("log"):
    os.mkdir("log")
if( os.path.exists(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log')) ):
    os.remove(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
logger = logging.getLogger(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
logger.setLevel(10)
logger_fh = logging.FileHandler(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
logger.addHandler(logger_fh)

# FastAPI
app = FastAPI()
print('[{}] time {} | 推論サーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
logger.info('[{}] time {} | 推論サーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

class ImageData(BaseModel):
    """
    画像データのリクエストボディ
    """
    image: Any

@app.get("/")
async def root():
    return 'Hello API Server!\n'

@app.get("/health")
async def health():
    return {"health": "ok"}

@app.get("/metadata")
async def metadata():
    return

@app.post("/predict")
async def predict(
    img_data: ImageData,        # リクエストボディ    
):
    print('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    logger.info('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

    # base64 -> Pillow への変換
    img_data.image = conv_base64_to_pillow(img_data.image)

    # OpenCV を用いて背景除去
    _, img_none_bg_pillow = graph_cut(img_data.image)

    # Pillow -> base64 への変換
    img_none_bg_base64 = conv_pillow_to_base64(img_none_bg_pillow)

    # 非同期処理の効果を明確化するためにあえて sleep 処理
    sleep(1)

    # レスポンスデータ設定
    print('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    logger.info('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

    return {
        "status": "ok",
        "img_none_bg_base64" : img_none_bg_base64,
    }
