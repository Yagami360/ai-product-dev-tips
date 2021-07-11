import os

class ProxyServerConfig:
    # クラス変数
    predict_server_url = os.getenv("PREDICT_SERVER_URL", "predict-container:5001")

class PredictServerConfig:
    # クラス変数
    binary_threshold = int(os.getenv("BINARY_THRESHOLD", "250"))

class ResidConfig:
    # クラス変数
    host="redis-container"
    port="6379"
    database_id=0
