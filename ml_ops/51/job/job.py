import os
import sys
from datetime import datetime
from time import sleep
import random
import logging

# logger
if not os.path.isdir("log"):
    os.mkdir("log")
#if( os.path.exists(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log')) ):
#    os.remove(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
logger = logging.getLogger(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
logger.setLevel(10)
logger_fh = logging.FileHandler(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
logger.addHandler(logger_fh)

#
if __name__ == "__main__":
    logger.info('[{}] time {} | 処理開始しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    sleep(10)
    if( random.uniform(0, 1) <= 0.9 ):
        logger.info('[{}] time {} | 正常終了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
        sys.exit(0)
    else:
        logger.info('[{}] time {} | 異常終了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
        sys.exit(1)
