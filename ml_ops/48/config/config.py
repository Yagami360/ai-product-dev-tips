import os

class ProxyServerConfig:
    # クラス変数
    tmp_dir = os.getenv("TMP_DIR", "tmp")
    debug = bool(os.getenv("DEBUG", "False"))

class BatchServerConfig:
    # クラス変数
    n_workers=2
    polling_time=1  # ポーリング間隔時間 (sec単位)
    #polling_time=5  # ポーリング間隔時間 (sec単位)

class PredictServerConfig:
    # クラス変数
    host="predict-container"
    port="5001"