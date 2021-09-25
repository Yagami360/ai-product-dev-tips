import os

class ResidConfig:
    # クラス変数
    host="redis-server"
    port="6379"
    database_id=0

class ProxyServerConfig:
    # クラス変数
    cache_dir = os.getenv("CACHE_DIR", "/redis/tmp")
    debug = bool(os.getenv("DEBUG", "False"))

class BatchServerConfig:
    # クラス変数
    n_workers=int(os.getenv("N_WORKERS", "2"))
    polling_time=int(os.getenv("POLLING_TIME", "5"))  # ポーリング間隔時間 (sec単位)
 
class PredictServerConfig:
    # クラス変数
    host="predict-video-server"
    port="5001"
    cache_dir = os.getenv("CACHE_DIR", "tmp")
    video_height = int(os.getenv("VIDEO_HEIGHT", "300"))
    video_width = int(os.getenv("VIDEO_WIDTH", "168"))
