import os
import sys
import logging
import time
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import asyncio
import requests

from config import BatchServerConfig
sys.path.append(os.path.join(os.getcwd(), '..'))
from utils.img_utils import conv_base64_to_pillow, conv_pillow_to_base64
from mysql_utils.setting import global_session, get_context_session
from mysql_utils import crud
from mysql_utils import converter
from mysql_utils.models import JobTable

#--------------------------
# logger
#--------------------------
if not os.path.isdir("log"):
    os.mkdir("log")
if( os.path.exists(os.path.join("log", __name__ + '.log')) ):
    os.remove(os.path.join("log", __name__ + '.log'))

logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler(os.path.join("log", __name__ + '.log'))
logger.addHandler(logger_fh)
logger.info("{} {} {} start batch server".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", __name__))

def predict(table: JobTable):
    """
    推論処理
    """
    start_time = time.time()
    #img_pillow = conv_base64_to_pillow(table.image_in)
    #img_gray_pillow = img_pillow.convert("L")
    #img_gray_pillow.point(lambda x: 0 if x < BatchServerConfig.threshold else x)
    #img_out_base64 = conv_pillow_to_base64(img_gray_pillow)
    img_out_base64 = None
    elapsed_time = 1000 * (time.time() - start_time)
    return img_out_base64, elapsed_time

def predict_batch(tables: JobTable):
    """
    バッチ単位での推論処理
    """
    img_out_base64_batch = []
    elapsed_time_batch = []
    for table in tables:
        start_time = time.time()
        #img_pillow = conv_base64_to_pillow(table.image_in)
        #img_gray_pillow = img_pillow.convert("L")
        #img_gray_pillow.point(lambda x: 0 if x < BatchServerConfig.threshold else x)
        #img_out_base64 = conv_pillow_to_base64(img_gray_pillow)
        img_out_base64 = None
        elapsed_time = 1000 * (time.time() - start_time)

        img_out_base64_batch.append(img_out_base64)
        elapsed_time_batch.append(elapsed_time)

    return img_out_base64_batch, elapsed_time_batch

def process_job():
    """
    MySQL から取得したジョブデータでバッチ単位での推論処理を行い、推論結果を MySQL に保存する
    """
    # MySQL から全テーブルデータ取得
    with get_context_session() as session:
        tables = crud.select_all(session)

    # バッチ単位での推論処理
    img_out_base64_batch = []
    elapsed_time_batch = []
    with ThreadPoolExecutor(BatchServerConfig.n_workers) as executor:
        #img_out_base64_batch, elapsed_time_batch = executor.map(predict_batch, tables)
        results = executor.map(predict, tables)
        for result in results:
            img_out_base64_batch.append(result[0])
            elapsed_time_batch.append(result[1])

    print( "len(tables)", len(tables) )
    print( "len(img_out_base64_batch)", len(img_out_base64_batch) )
    print( "len(elapsed_time_batch)", len(elapsed_time_batch) )

    # MySQL に推論結果を保存する
    with get_context_session() as session:
        for i, table in enumerate(tables):
            #crud.insert(session=session, job_id=table.job_id, image_in=table.image_in, image_out=img_out_base64_batch[i], elapsed_time=elapsed_time_batch[i])
            #crud.insert(session=session, job_id=table.job_id, elapsed_time=elapsed_time_batch[i])

            selct_table = crud.select_job_id(session=session, job_id=table.job_id)
            selct_table.elapsed_time = elapsed_time_batch[i]
            session.commit()
            #session.refresh(JobTable)

    return

if __name__ == "__main__":
    time.sleep(BatchServerConfig.init_wait_time)
    while True:
        process_job()

        # ポーリング間隔
        time.sleep(BatchServerConfig.polling_time)
