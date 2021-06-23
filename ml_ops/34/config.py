# coding=utf-8
class MySQLConfig:
    # クラス変数
    username="root"
    password="tShH78;g"
    host="localhost"
    port="3306"
    db_name="test_db"
    database_url = f"mysql+pymysql://{username}:{password}@{host}/{db_name}?charset=utf8"
