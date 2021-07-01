# coding=utf-8
import os

class BatchServerConfig:
    # クラス変数
    n_workers=4
    init_wait_time=1        # 初回起動待ち時間 (sec単位)
    polling_time=10         # ポーリング間隔時間 (sec単位)
    threshold=210
