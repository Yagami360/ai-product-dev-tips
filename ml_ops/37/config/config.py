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

class APIConfig:
    # クラス変数
    threshold=210

class BatchServerConfig:
    # クラス変数
    n_workers=2
    polling_time=1  # ポーリング間隔時間 (sec単位)
    #polling_time=5  # ポーリング間隔時間 (sec単位)
