# coding=utf-8
import os

class MySQLConfig:
    # クラス変数
    #username="root"        # root ユーザーを使用する場合は、"root" を設定
    username="mysql"        # MySQL サーバーの環境変数 `MYSQL_USER` を設定した場合は、`MYSQL_USER` と同じ値を設定
    password="password"     # root ユーザーの場合は、MySQL サーバーの環境変数 `MYSQL_ROOT_PASSWORD` と同じ値を設定。新規ユーザーを作成する場合は、MySQL サーバーの環境変数 `MYSQL_PASSWORD` と同じ値を設定
    db_name="test_db"       # MySQL サーバーの環境変数 `MYSQL_DATABASE` を設定した場合は、`MYSQL_DATABASE` と同じ値を設定
    host="localhost"        # デフォルトでは、"localhost"
    #host="0.0.0.0"
    #host="mysql_server"
    port="3306"             # デフォルトでは、3306
    database_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}?charset=utf8"
    #database_url = f"mysql+pymysql://{username}:{password}@{host}/{db_name}?charset=utf8"
    
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