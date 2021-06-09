import os
import asyncio
from datetime import datetime
from time import sleep
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

import sys
sys.path.append(os.path.join(os.getcwd(), '../utils'))
from utils import conv_base64_to_pillow, conv_pillow_to_base64

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler( __name__ + '.log')
logger.addHandler(logger_fh)

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

@app.post("/api")
async def api(
    img_data: ImageData,        # リクエストボディ    
):
    print('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    logger.info('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

    # base64 -> Pillow への変換
    img_data.image = conv_base64_to_pillow(img_data.image)

    sleep(10)

    print('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    logger.info('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    return
