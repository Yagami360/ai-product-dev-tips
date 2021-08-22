
import os

class PredictServerConfig:
    # クラス変数
    #use_https=bool(os.getenv("USE_HTTPS", False))
    binary_threshold = int(os.getenv("BINARY_THRESHOLD", "250"))
