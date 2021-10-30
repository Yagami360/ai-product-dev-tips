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
if not os.path.isdir("log"):
    os.mkdir("log")
if( os.path.exists(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log')) ):
    os.remove(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
logger = logging.getLogger(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
logger.setLevel(10)
logger_fh = logging.FileHandler(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
logger.addHandler(logger_fh)

def polling():
    """
    Redis のキューを定期的にポーリングして、Cloud Monitorning に書き込む
    """
    #--------------------
    # カスタム指標を作成
    # 参考コード : https://cloud.google.com/monitoring/custom-metrics/creating-metrics?hl=ja
    #--------------------
    metrics_client = monitoring_v3.MetricServiceClient()

    # カスタム指標が既に存在する場合は削除（上書き不可のため）
    for descriptor in metrics_client.list_metric_descriptors(name="projects/" + MonitoringServerConfig.project_id):
        if(descriptor.name == "projects/" + MonitoringServerConfig.project_id + "/metricDescriptors/" + "custom.googleapis.com/" + MonitoringServerConfig.metric_name ):
            metrics_client.delete_metric_descriptor(name=descriptor.name)
            logger.info("{} {} {} Deleted metrics={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, descriptor.name))

    # create_metric_descriptor() メソッドの metric_descriptor 引数
    metric_descriptor = ga_metric.MetricDescriptor()
    metric_descriptor.type = "custom.googleapis.com/" + MonitoringServerConfig.metric_name         # 使用できるプレフィックスは custom.googleapis.com/ と external.googleapis.com/prometheus 
    metric_descriptor.metric_kind = ga_metric.MetricDescriptor.MetricKind.GAUGE                    #
    metric_descriptor.value_type = ga_metric.MetricDescriptor.ValueType.INT64                      #
    metric_descriptor.description = "job_ids in redis queue."

    # metric_descriptor.labels に設定するラベル
    labels = ga_label.LabelDescriptor()
    labels.key = MonitoringServerConfig.metric_name + "_label"
    labels.value_type = ga_label.LabelDescriptor.ValueType.STRING
    labels.description = "label for " + MonitoringServerConfig.metric_name
    metric_descriptor.labels.append(labels)

    # metrics_client.create_metric_descriptor() で、カスタム指標の記述子（descriptor）を作成
    descriptor = metrics_client.create_metric_descriptor(name= "projects/" + MonitoringServerConfig.project_id, metric_descriptor=metric_descriptor)
    logger.info("{} {} {} Created metrics={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, descriptor.name))

    # モニタリング指標に書き込むための TimeSeries オブジェクトの作成
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/" + MonitoringServerConfig.metric_name
    series.resource.type = MonitoringServerConfig.metric_resource_type
    if(MonitoringServerConfig.metric_resource_type == "global"):       # https://cloud.google.com/monitoring/api/resources?hl=ja#tag_global
        series.resource.labels["project_id"] = MonitoringServerConfig.project_id
    elif(MonitoringServerConfig.metric_resource_type == "k8s_pod"):    # https://cloud.google.com/monitoring/api/resources?hl=ja#tag_k8s_pod
        series.resource.labels["project_id"] = MonitoringServerConfig.project_id
        series.resource.labels["location"] = "us-central1-f"
        series.resource.labels["cluster_name"] = "monitering-cluster"       
        series.resource.labels["namespace_name"] = "default"
        series.resource.labels["pod_name"] = "monitering-server-pod"
    else:
        series.resource.labels["project_id"] = MonitoringServerConfig.project_id

    while True:
        # Redis キューの数を取得
        n_queues_in_redis = redis_client.llen('job_id')
        logger.info("{} {} {} n_queues_in_redis={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, n_queues_in_redis))

        # 横軸の interval 設定
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        interval = monitoring_v3.TimeInterval({"end_time": {"seconds": seconds, "nanos": nanos}})
        
        # Cloud Monitoring へ書き込み
        point = monitoring_v3.Point({
            "interval": interval, 
            "value": {
                "int64_value": n_queues_in_redis     # descriptor.value_type = ga_metric.MetricDescriptor.ValueType.INT64 の場合は、"int64_value" である必要がある。（https://cloud.google.com/monitoring/api/ref_v3/rpc/google.monitoring.v3#google.monitoring.v3.TypedValue）
            }
        })
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
