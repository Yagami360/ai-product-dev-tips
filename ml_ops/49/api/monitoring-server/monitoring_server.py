import os
import logging
from datetime import datetime
import time
from time import sleep
from concurrent.futures import ProcessPoolExecutor
import asyncio

# Cloud Monitoring API
from google.cloud import monitoring_v3
from google.api import metric_pb2 as ga_metric
from google.api import label_pb2 as ga_label

# 自作モジュール
import sys
sys.path.append(os.path.join(os.getcwd(), '../config'))
from config import MonitoringServerConfig

sys.path.append(os.path.join(os.getcwd(), '../redis'))
from redis_client import redis_client

# logger
if( os.path.exists(__name__ + '.log') ):
    os.remove(__name__ + '.log')
logger = logging.getLogger(__name__)
logger.setLevel(10)
logger_fh = logging.FileHandler( __name__ + '.log')
logger.addHandler(logger_fh)

def polling():
    """
    Redis のキューを定期的にポーリングして、Cloud Monitorning に書き込む
    """
    #--------------------
    # カスタム指標を作成
    #--------------------
    metrics_client = monitoring_v3.MetricServiceClient()

    #for descriptor in metrics_client.list_metric_descriptors(name="projects/" + MonitoringServerConfig.project_id):
    #metrics_client.delete_metric_descriptor(name=descriptor_name)

    # 指標記述子
    descriptor = ga_metric.MetricDescriptor()
    descriptor.type = "custom.googleapis.com/" + MonitoringServerConfig.metric_name         # 使用できるプレフィックスは custom.googleapis.com/ と external.googleapis.com/prometheus 
    descriptor.metric_kind = ga_metric.MetricDescriptor.MetricKind.GAUGE                    #
    descriptor.value_type = ga_metric.MetricDescriptor.ValueType.DOUBLE                      #
    descriptor.description = "joj_ids in redis queue."

    # descriptor.labels に設定するラベル
    labels = ga_label.LabelDescriptor()
    #labels.key = MonitoringServerConfig.metric_name                     # monitoring_v3.Point() で指定する {"interval": interval, "value": {key:value} }
    labels.key = "TestLabel"
    labels.value_type = ga_label.LabelDescriptor.ValueType.STRING
    labels.description = "This is a test label"
    descriptor.labels.append(labels)

    # 
    descriptor = metrics_client.create_metric_descriptor(
        name= "projects/" + MonitoringServerConfig.project_id,
        metric_descriptor=descriptor
    )
    logger.info("{} {} {} Created metrics={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, descriptor.name))

    # モニタリング指標に書き込むための TimeSeries オブジェクトの作成
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/" + MonitoringServerConfig.metric_name
    series.resource.type = MonitoringServerConfig.metric_resource_type
    series.resource.labels["project_id"] = MonitoringServerConfig.project_id

    while True:
        # Redis キューの数を取得
        n_queues_in_redis = redis_client.llen('job_id')
        logger.info("{} {} {} n_queues_in_redis={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, n_queues_in_redis))

        # モニタリング指標に書き込み
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        interval = monitoring_v3.TimeInterval(
            {"end_time": {"seconds": seconds, "nanos": nanos}}
        )
        point = monitoring_v3.Point({"interval": interval, "value": {"double_value": n_queues_in_redis}})
        series.points = [point]        
        metrics_client.create_time_series(name="projects/" + MonitoringServerConfig.project_id, time_series=[series])

        # ポーリング間隔
        sleep(MonitoringServerConfig.polling_time)

    return

if __name__ == "__main__":
    executor = ProcessPoolExecutor(MonitoringServerConfig.n_workers)
    loop = asyncio.get_event_loop()

    for _ in range(MonitoringServerConfig.n_workers):
        # loop.run_in_executor() により、実際の処理 _loop() を別スレッドで実行するコルーチンがを生成
        # 作成したコルーチンを asyncio.ensure_future で Task 化
        # executor として、デフォルトの ThreadPoolExecutor ではなく ProcessPoolExecutor を使用
        asyncio.ensure_future(loop.run_in_executor(executor, polling))

    # loop.stop()が呼ばれるまでループし続ける
    loop.run_forever()
