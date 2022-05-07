# coding=utf-8
import os

class MySQLConfig:
    # クラス変数
    username=os.getenv("MYSQL_USER")
    password=os.getenv("MYSQL_PASSWORD")
    db_name=os.getenv("MYSQL_DATABASE")
    host=os.getenv("MYSQL_HOST")
    port=int(os.getenv("MYSQL_PORT", 3306))
    database_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}?charset=utf8"
