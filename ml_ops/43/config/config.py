import os

class ResidConfig:
    # クラス変数
    #host="0.0.0.0"
    host="redis-container"
    port="6379"
    database_id=0

class PredictServerSyncConfig:
    # クラス変数
    host=os.getenv("HOST", "predict-container-sync")
    port=os.getenv("PORT", "5010")
    grab_cut_iters = int(os.getenv("GRAB_CUT_ITERS", "1"))

class PredictServerAsyncConfig:
    # クラス変数
    host=os.getenv("HOST", "predict-container-async")
    port=os.getenv("PORT", "5011")
    grab_cut_iters = int(os.getenv("GRAB_CUT_ITERS", "10"))

class BatchServerConfig:
    # クラス変数
    n_workers=2
    sleep_time_init=1  # ポーリング間隔時間 (sec単位)
    polling_time=1  # ポーリング間隔時間 (sec単位)
    #polling_time=5  # ポーリング間隔時間 (sec単位)

class ProxyServerConfig:
    # クラス変数
    host=os.getenv("HOST", "proxy-container")
    port=os.getenv("PORT", "5010")
