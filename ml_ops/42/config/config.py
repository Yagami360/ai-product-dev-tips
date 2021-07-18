import os

class PredictServerConfig:
    # クラス変数
    grab_cut_iters = int(os.getenv("GRAB_CUT_ITERS", "5"))
