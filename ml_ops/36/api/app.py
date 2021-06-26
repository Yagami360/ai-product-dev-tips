# coding=utf-8
import os
import sys
import argparse
from datetime import datetime
import logging
import uuid

from fastapi import FastAPI

# 自作モジュール
from utils.logger import log_base_decorator

sys.path.append(os.path.join(os.getcwd(), '../'))
from mysql_utils.setting import global_session, get_context_session
from mysql_utils import crud
from mysql_utils import converter

#--------------------------
# logger
#--------------------------
if not os.path.isdir("log"):
    os.mkdir("log")
if( os.path.exists(os.path.join("log", __name__ + '.log')) ):
    os.remove(os.path.join("log", __name__ + '.log'))

logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler(os.path.join("log", __name__ + '.log'))
logger.addHandler(logger_fh)
logger.info("{} {} {} start api server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", __name__))

#--------------------------
# FastAPI
#--------------------------
app = FastAPI()

users_db = {
    "name" : {
        0 : "user1",
        1 : "user2",
        2 : "user3",
    },
    "age" : {
        0 : "24",
        1 : "30",
        2 : "18",
    },
}

#--------------------------
# MySQL (SQLAlchemy)
#--------------------------
crud.init()

#======================================
# GET method
#======================================
@app.get("/")
def root():
    return 'Hello Flask-API Server!\n'

@log_base_decorator(logger=logger)
def _health():
    return {"health": "ok"}

@app.get("/health")
def health():
    return _health()

@log_base_decorator(logger=logger)
def _metadata():
    return users_db

@app.get("/metadata")
def metadata():
    return _metadata()

@app.get("/users_name/{users_id}")
def get_user_name_by_path_parameter(
    users_id: int,  # パスパラメーター
):
    return users_db["name"][users_id]

@app.get("/users_name/")
def get_user_name_by_query_parameter(
    users_id: int, # クエリパラメーター
):
    return users_db["name"][users_id]

@app.get("/users/{attribute}")
def get_user_by_path_and_query_parameter(
    attribute: str, # パスパラメーター
    users_id: int,  # クエリパラメーター
):
    return users_db[attribute][users_id]

@app.get("/log/{log_id}")
def get_log(
    log_id: int, # パスパラメーター
):
    with get_context_session() as session:
        data = crud.select_all(session)
    return converter.convert_table_to_json(data)

#======================================
# POST method
#======================================
from pydantic import BaseModel
# `pydantic.BaseModel` 継承クラスでリクエストボディを定義
class UserData(BaseModel):
    id: int
    name: str
    age: str

@log_base_decorator(logger=logger)
def _add_user(
    job_id: str,
    user_data: UserData,
):
    users_db["name"][user_data.id] = user_data.name
    users_db["age"][user_data.id] = user_data.age

    # MySQL にログデータ追加
    with get_context_session() as session:
        log = {
            "job_id" : job_id,
            "id": user_data.id,
            "name": user_data.name, 
            "age": user_data.age,
            "users_db" : users_db,
        }
        crud.insert(session=session, id=job_id, data=log)

    return users_db

@app.post("/add_users/")
def add_user(
    user_data: UserData,     # リクエストボディ
):
    job_id = str(uuid.uuid4())[:6]
    return _add_user(job_id=job_id, user_data=user_data)
