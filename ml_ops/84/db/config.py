# coding=utf-8
class MySQLConfig:
    # クラス変数
    username="postgres"
    password="1234"
    host="localhost"
    port="5432"
    db_name="postgres_db"
    #database_url = f"mysql+pymysql://{username}:{password}@{host}/{db_name}?charset=utf8"
    database_url = f"postgresql://localhost:{port}/{db_name}?user={username}&password={password}"
