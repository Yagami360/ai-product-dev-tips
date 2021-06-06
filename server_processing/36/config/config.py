import os

class ResidConfig:
    # クラス変数
    #host="0.0.0.0"
    host="redis_server"
    port=6379
    database_id=0

class BatchServerConfig:
    # クラス変数
    n_workers=2
