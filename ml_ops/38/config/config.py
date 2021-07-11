import os

class ProxyServerConfig:
    # クラス変数
    predict_server1_url = os.getenv("PREDICT_SERVER1_URL", "predict-container1:5001")
    predict_server2_url = os.getenv("PREDICT_SERVER2_URL", "predict-container2:5002")
    predict_server3_url = os.getenv("PREDICT_SERVER3_URL", "predict-container3:5003")

class PredictServerConfig:
    # クラス変数
    binary_threshold = int(os.getenv("BINARY_THRESHOLD", "250"))
