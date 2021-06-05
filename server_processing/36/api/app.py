import asyncio
from datetime import datetime
from time import sleep
import logging

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler( __name__ + '.log')
logger.addHandler(logger_fh)


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
async def api():
    sleep(10)
    return
    