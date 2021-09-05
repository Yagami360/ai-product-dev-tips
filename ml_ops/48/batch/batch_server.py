import os
import logging
from datetime import datetime
from time import sleep
from concurrent.futures import ProcessPoolExecutor
import asyncio
import requests

import sys
sys.path.append(os.path.join(os.getcwd(), '../redis'))
from redis_client import redis_client

sys.path.append(os.path.join(os.getcwd(), '../config'))
from config import BatchServerConfig
from config import PredictServerConfig
from config import ProxyServerConfig

# logger
if not os.path.isdir("log"):
    os.mkdir("log")
"""
if( os.path.exists(os.path.join("log", 'app.log')) ):
    os.remove(os.path.join("log", 'app.log'))
"""
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler(os.path.join("log", 'app.log'))
logger.addHandler(logger_fh)
logger.info("{} {} start batch server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO"))

def polling():
    """
    ローカルディスク上のキャッシュデータを定期的にポーリングして、API サーバーにリクエスト処理を送信する
    """
    while True:
        # Redis キューの末端からデータを pop
        job_id = redis_client.rpop('job_id')
        if job_id is not None:
            job_id = job_id.decode()
            
            # job_id に対応したファイルパスを取得
            in_file_path = redis_client.get(job_id + "_in_file_path").decode()
            logger.info('[{}] time {} | job_id={}, in_file_path="{}" を pop しました'.format(__name__, f"{datetime.now():%H:%M:%S}", job_id, in_file_path))

            # 推論サーバーのヘルスチェック
            try:
                health = requests.get( "http://" + PredictServerConfig.host + ":" + PredictServerConfig.port + "/health" ).json()
                logger.info('[{}] time {} | health {}'.format(__name__, f"{datetime.now():%H:%M:%S}", health))
            except Exception as e:
                logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))

            # 推論サーバーにリクエスト処理
            try:
                files = { 'file': (in_file_path.split("/")[-1], open(in_file_path,"rb"), 'video/mp4') }
                api_responce = requests.post( "http://" + PredictServerConfig.host + ":" + PredictServerConfig.port + "/predict", files=files )
                api_responce = api_responce.json()
                logger.info('[{}] time {} | api_responce["status"] {}'.format(__name__, f"{datetime.now():%H:%M:%S}", api_responce["status"]))
            except Exception as e:
                print( "Exception : ", e )
                logger.info('[{}] time {} | Exception {}'.format(__name__, f"{datetime.now():%H:%M:%S}", e))

            # 出力動画データのファイルパスを保管
            out_file_path = os.path.join(ProxyServerConfig.cache_dir, job_id, "output.mp4" )
            redis_client.set("job_id" + "_out_file_path", out_file_path)

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
