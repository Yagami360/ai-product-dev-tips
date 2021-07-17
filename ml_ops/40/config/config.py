import os

class ProxyServerConfig:
    # クラス変数
    predict_server_url = os.getenv("PREDICT_SERVER_URL", "predict-container1:5010")

class PredictServerConfig:
    # クラス変数
    grab_cut_iters = int(os.getenv("GRAB_CUT_ITERS", "5"))
