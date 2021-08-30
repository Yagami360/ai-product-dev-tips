import os
import logging
from datetime import datetime
import time
import asyncio
import time
import requests
import uuid
from PIL import Image
import shutil
from typing import List

from fastapi import FastAPI
from fastapi import UploadFile, File, HTTPException
from fastapi import BackgroundTasks
from pydantic import BaseModel
from typing import Any, Dict

import sys
from config import FastAPIServerConfig
from utils.utils import conv_base64_to_pillow, conv_pillow_to_base64
from utils.logger import log_base_decorator, log_decorator

if not os.path.isdir(FastAPIServerConfig.upload_dir):
    os.mkdir(FastAPIServerConfig.upload_dir)
    
# logger
if not os.path.isdir("log"):
    os.mkdir("log")
"""
if( os.path.exists(os.path.join("log", 'app.log')) ):
    os.remove(os.path.join("log", 'app.log'))
"""
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler(os.path.join("log", 'app.log'))
logger.addHandler(logger_fh)
logger.info("{} {} start api server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO"))

# Fast API
app = FastAPI()

#-----------------------------
# エンドポイント
#-----------------------------
@app.get("/")
def root():
    return 'Hello API Server!\n'

@log_base_decorator(logger=logger)
def _health():
    return {"health": "ok"},

@app.get("/health")
def health():
    return _health()

@app.get("/metadata")
def metadata():    
    return

@app.post("/upload_files")
async def upload_files(files: List[UploadFile] = File(...)):
    start_time = time.time()
    logger.info("{} {} {} {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START"))
    for file in files:
        try:
            with open(os.path.join(FastAPIServerConfig.upload_dir, file.filename),'wb+') as buffer:
                shutil.copyfileobj(file.file, buffer)
            responce = {
                "status": "ok",
                "file_name": file.filename,
                "file_path": os.path.join(FastAPIServerConfig.upload_dir,file.filename),
            }
        except Exception as e:
            responce = {
                "status": "ng",
                "file_name": None,
                "file_path": None,
            }
        finally:
            file.file.close()

    elapsed_time = 1000 * (time.time() - start_time)
    logger.info("{} {} {} {} elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", elapsed_time))
    return responce
