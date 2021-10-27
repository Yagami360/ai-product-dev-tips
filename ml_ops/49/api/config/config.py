import os

class ResidConfig:
    # クラス変数
    host=os.getenv("HOST", "redis-container")
    port=int(os.getenv("PORT", "6379"))
    database_id=int(os.getenv("DATABASE_ID", "0"))

class BatchServerConfig:
    # クラス変数
    n_workers=int(os.getenv("N_WORKERS", "1"))
    polling_time=int(os.getenv("POLLING_TIME", "5"))   # ポーリング間隔時間 (sec単位)

class PredictServerConfig:
    # クラス変数
    host="predict-container"
    port="5001"

class MonitoringServerConfig:
    # クラス変数
    project_id=os.getenv("PROJECT_ID", "my-project2-303004")
    n_workers=int(os.getenv("N_WORKERS", "1"))
    polling_time=int(os.getenv("POLLING_TIME", "5"))                        # ポーリング間隔時間 (sec単位)
    metric_name=os.getenv("METRIC_NAME", "n_queues_in_redis")               # モニタリング指標名
    metric_resource_type=os.getenv("METRIC_RESOURCE_TYPE", "global")        # モニタリング対象リソースタイプ 
