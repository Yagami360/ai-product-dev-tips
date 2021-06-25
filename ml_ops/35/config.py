# coding=utf-8
import os

"""
class MySQLConfig:
    # クラス変数
    username=os.getenv("MYSQL_USER")
    password=os.getenv("MYSQL_PASSWORD")
    host=os.getenv("MYSQL_HOST")
    port=int(os.getenv("MYSQL_PORT", 3306))
    db_name=os.getenv("MYSQL_DATABASE")
    database_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}?charset=utf8"
"""
class MySQLConfig:
    # クラス変数
    username="root"
    password="tShH78;g"
    host="localhost"
    port="3306"
    db_name="test_db"
    database_url = f"mysql+pymysql://{username}:{password}@{host}/{db_name}?charset=utf8"
