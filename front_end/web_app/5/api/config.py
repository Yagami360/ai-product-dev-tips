
import os

class PredictServerConfig:
    # クラス変数
    binary_threshold = int(os.getenv("BINARY_THRESHOLD", "250"))
    