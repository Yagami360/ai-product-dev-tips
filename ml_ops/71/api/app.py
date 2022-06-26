from fastapi import FastAPI

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

#======================================
# GET method
#======================================
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

#======================================
# POST method
#======================================
from pydantic import BaseModel
# `pydantic.BaseModel` 継承クラスでリクエストボディを定義
class UserData(BaseModel):
    id: int
    name: str
    age: str

@app.post("/add_users/")
def add_user(
    user_data: UserData,     # リクエストボディ
):
    users_db["name"][user_data.id] = user_data.name
    users_db["age"][user_data.id] = user_data.age
    return users_db
