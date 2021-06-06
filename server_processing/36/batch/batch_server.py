import os
import os
import logging
from datetime import datetime
from time import sleep
from concurrent.futures import ProcessPoolExecutor
import asyncio

import sys
sys.path.append(os.path.join(os.getcwd(), '../config'))
from config import BatchServerConfig
sys.path.append(os.path.join(os.getcwd(), '../redis'))
from redis_client import redis_client

# logger
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler( __name__ + '.log')
logger.addHandler(logger_fh)

def polling():
    """
    Redis のキューを定期的にポーリングして、API サーバーにリクエスト処理を送信する
    """
    while True:
        # Redis キューの末端からデータを pop
        job_id = redis_client.rpop('job_id')
        print('[{}] time {} | Job {} を pop しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id))
        logger.info('[{}] time {} | Job {} を pop しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id))

        # API サーバーにリクエスト処理
        pass

        # ポーリング間隔
        sleep(1)

    return

if __name__ == "__main__":
    executor = ProcessPoolExecutor(BatchServerConfig.n_workers)
    loop = asyncio.get_event_loop()

    for _ in range(BatchServerConfig.n_workers):
        # loop.run_in_executor() により、実際の処理 _loop() を別スレッドで実行するコルーチンがを生成
        # 作成したコルーチンを asyncio.ensure_future で Task 化
        # executor として、デフォルトの ThreadPoolExecutor ではなく ProcessPoolExecutor を使用
        asyncio.ensure_future(loop.run_in_executor(executor, polling))

    # loop.stop()が呼ばれるまでループし続ける
    loop.run_forever()
