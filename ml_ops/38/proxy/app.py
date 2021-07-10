import os
import logging
from datetime import datetime
from time import sleep
import asyncio
import uuid
from PIL import Image

from fastapi import FastAPI
from fastapi import BackgroundTasks
from pydantic import BaseModel
from typing import Any, Dict

import sys
sys.path.append(os.path.join(os.getcwd(), '../utils'))
from utils import conv_base64_to_pillow, conv_pillow_to_base64
from logger import log_base_decorator

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
    return {"health": "ok"}

@app.get("/health")
def health():
    return _health()

@app.get("/metadata")
def metadata():    
    return

@log_base_decorator(logger=logger)
def _predict(
    job_id: str,
    img_data: ImageData,
):
    # 
    img_base64 = img_data.image

    # 複数の Web-API に並列リクエスト


    return {
        "status": "ok",
    }


@app.post("/predict")
async def predict(
    img_data: ImageData,                # リクエストボディ
):
    # job_id を自動生成
    job_id = str(uuid.uuid4())[:6]
    return _predict(job_id=job_id, img_data=img_data)
