import asyncio

from fastapi import FastAPI
from fastapi import BackgroundTasks
from pydantic import BaseModel

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

# `pydantic.BaseModel` 継承クラスでリクエストボディを定義
class UserData(BaseModel):
    id: int
    name: str
    age: str


@app.get("/")
def root():
    return 'Hello Flask-API Server!\n'

@app.get("/health")
def health():
    return {"health": "ok"}

@app.get("/metadata")
def metadata():
    return users_db

@app.get("/users_name/{users_id}")
async def get_user_name_by_path_parameter(
    users_id: int,  # パスパラメーター
):
    return users_db["name"][users_id]

@app.get("/users_name/")
async def get_user_name_by_query_parameter(
    users_id: int, # クエリパラメーター
):
    return users_db["name"][users_id]

@app.get("/users/{attribute}")
async def get_user_by_path_and_query_parameter(
    attribute: str, # パスパラメーター
    users_id: int,  # クエリパラメーター
):
    return users_db[attribute][users_id]

@app.post("/add_users/")
async def add_user(
    user_data: UserData,     # リクエストボディ
):
    users_db["name"][user_data.id] = user_data.name
    users_db["age"][user_data.id] = user_data.age
    return users_db
