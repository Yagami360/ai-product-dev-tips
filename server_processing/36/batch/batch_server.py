import os
import logging
from datetime import datetime
from time import sleep
from concurrent.futures import ProcessPoolExecutor
import asyncio
import requests

import sys
sys.path.append(os.path.join(os.getcwd(), '../config'))
from config import BatchServerConfig
from config import APIServerConfig

sys.path.append(os.path.join(os.getcwd(), '../redis'))
from redis_client import redis_client
from redis_utils import get_image_pillow_redis, get_image_base64_redis

sys.path.append(os.path.join(os.getcwd(), '../utils'))
from utils import conv_base64_to_pillow, conv_pillow_to_base64

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

        if job_id is not None:
            # job_id に対応した 画像データを取得
            img_base64 = get_image_base64_redis( redis_client=redis_client, key_name=job_id )

            # Resdis の画像データ削除
            #redis_client.delete(job_id)

            # API サーバーにリクエスト処理
            try:
                api_msg = {'image': img_base64}
                api_responce = requests.post( "http://" + APIServerConfig.host + ":" + APIServerConfig.port + "/api", json=api_msg )
                api_responce = api_responce.json()
                print( "api_responce : ", api_responce )
                logger.info('[{}] time {} | api_responce {}'.format(__name__, f"{datetime.now():%H:%M:%S}", api_responce))
            except Exception as e:
                print( "Exception : ", e )
                logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))

        # ポーリング間隔
        sleep(BatchServerConfig.polling_time)

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
