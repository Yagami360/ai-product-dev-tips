# 【GCP】Cloud Monitoring（旧 Stackdriver Monitoring）にカスタム指標を書き込む（FastAPI + uvicorn + gunicorn + redis + バッチサーバー + モニタリングサーバー + docker での構成）

Cloud Monitoring（旧 Stackdriver Monitoring）は、各種インフラリソースやアプリケーションのパフォーマンスを監視する GCP サービスであるが、アプリケーション固有のカスタム指標のモニタリングも行うことができる。

<img src="https://user-images.githubusercontent.com/25688193/139069365-bdc1754d-e0fe-413b-a566-a0a830bb1165.png" width="800"><br>

ここでは上図のように、「プロキシサーバ・バッチサーバ・モニタリングサーバー・Redis サーバー・推論サーバー」から構成される非同期 API において、カスタム指標として、Redis に保存されている job_id のキュー数を採用し、Cloud Monitoring への書き込む処理を行う。

尚、今回の構成例では、Redis に保存されている job_id のキュー数を無限ループでポーリングするモニタリングサーバーなるものを新規に追加し、モニタリングサーバー内で Python の Cloud Monitoring API を用いて、Cloud Monitoring への書き込む処理を行っているが、必ずしもモニタリングサーバーなるものを新規に追加する必要はないことに注意

> この Cloud Monitoring へのカスタム指標を書き込み処理の応用例としては、k8s の外部メトリックでのオートスケール機能と併用して、GKE で構成した非同期 API において、Redis のキュー数に応じてオートスケールするようなシステムが考えられる。詳細は「[【GKE】Cloud Monitoring でのカスタム指標を k8s の外部メトリックとしてオートスケールする](https://github.com/Yagami360/MachineLearning_Tips/tree/master/ml_ops/50)」を確認のこと

## ■ 使用法

1. Monitoring API を有効化する<br>
    ```sh
    $ gcloud services enable monitoring
    ```

1. サービスアカウントを作成する<br>
    Python の Cloud Monitoring API を用いて、Cloud Monitoring にアクセスする際に、Cloud Monitoring への IAM 権限が必要になるので、Cloud Monitoring への IAM 権限が付与されたサービスアカウントを作成する
    ```sh
    # サービスアカウント作成権限のある個人アカウントに変更
    $ gcloud auth login

    # サービスアカウントに必要な権限を付与する
    $ gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/monitoring.admin"

    # サービスアカウントの秘密鍵 (json) を生成する
    $ mkdir -p ${ROOT_DIR}/api/key
    $ gcloud iam service-accounts keys create ${ROOT_DIR}/api/key/${SERVICE_ACCOUNT_NAME}.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
    ```

    > 本項目の構成では、monitoring サーバーの docker コンテナ内で Cloud Monitoring API を用いて Cloud Monitoring にアクセスするので、API 用のサービスアカウントを新たに作成して、そのサービスアカウントに Cloud Monitoring への IAM 権限が付与し、monitoring サーバーの docker コンテナ内でそのサービスアカウントに切り替えるようにしている

    > docker コンテナ内ではなく、ホスト PC 内で Cloud Monitoring API を用いて Cloud Monitoring にアクセスする場合は、個人アカウントに Cloud Monitoring への IAM 権限を追加するだけでよい

    ここで、作成したサービスアカウントの秘密鍵 (json) は、Cloud Monitoring API を用いて Cloud Monitoring にアクセスするモジュール（今の場合は Monitoring サーバー）に認証させる必要があるが、この処理は、`docker-compose.yml` 内の `environment` タグに `GOOGLE_APPLICATION_CREDENTIALS: "/api/key/cloud-monitoring.json"` を設定して行うようにしている。

    > `export GOOGLE_APPLICATION_CREDENTIALS = "json鍵へのパス"` の形式でもよい

    - `docker-compose.yml` のコード抜粋
        ```yaml
        monitoring-server:
            container_name: monitoring-container
            image: monitoring-server-image
            build:
            context: "api/monitoring-server/"
            dockerfile: Dockerfile_dev
            volumes:
                - ${PWD}/api/monitoring-server:/api/monitoring-server
                - ${PWD}/api/redis:/api/redis
                - ${PWD}/api/config:/api/config
                - ${PWD}/api/key:/api/key
            tty: true
            environment:
                TZ: "Asia/Tokyo"
                LC_ALL: C.UTF-8
                LANG: C.UTF-8
                GOOGLE_APPLICATION_CREDENTIALS: "/api/key/cloud-monitoring.json"
            command: bash -c "python monitoring_server.py"
            depends_on:
                - redis-server
                - batch-server
                - predict-server
        ```

1. redis サーバーのコード [api/redis/redis_client.py](https://github.com/Yagami360/MachineLearning_Tips/blob/master/ml_ops/49/api/redis/redis_client.py) を作成する<br>
    Redis の Python API を用いて Redis サーバーに接続するためのコードを作成する。<br>
    本項目のコア部分ではないので、詳細は割愛する。

1. プロキシサーバーのコード [api/proxy-server/app.py](https://github.com/Yagami360/MachineLearning_Tips/blob/master/ml_ops/49/api/proxy-server/app.py)  を作成する<br>
    プロキシサーバでは、FastAPI を用いて、推論リクエストをジョブIDとして定義し、Redis のキューにジョブIDを push している。<br>
    本項目のコア部分ではないので、詳細は割愛する。

1. バッチサーバーのコード [api/batch-server/batch_server.py](https://github.com/Yagami360/MachineLearning_Tips/blob/master/ml_ops/49/api/batch-server/batch_server.py)  を作成する<br>
    バッチサーバーでは、Redis のデータを定期的にポーリングし、データがあれば推論サーバーにリクエスト処理する。その後、推論サーバーからのレスポンスデータを Redis に保存する。<br>
    バッチサーバーでのポーリング処理は、`asyncio` と `concurrent.futures.ProcessPoolExecutor` を使用した並列処理で行っている<br>
    本項目のコア部分ではないので、詳細は割愛する。

1. 推論サーバーのコード [api/predict-server/app.py](https://github.com/Yagami360/MachineLearning_Tips/blob/master/ml_ops/49/api/predict-server/app.py) を作成する<br>
    ここでは例えば、OpenCV の `cv2.grabCut()` を用いた推論サーバーを構築する。機械学習 API の場合は、この推論サーバーの部分が機械学習モデルを使用した推論処理になる。<br>
    本項目のコア部分ではないので、詳細は割愛する。

1. モニタリングサーバーのコード [api/monitoring-server/monitoring_server.py](https://github.com/Yagami360/MachineLearning_Tips/blob/master/ml_ops/49/api/monitoring-server/monitoring_server.py) を作成する<br>
    本項目のコア部分。Python の Cloud Monitoring API を用いて、モニタリング指標を書き込む

    ```python
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
                    "int64_value": n_queues_in_redis     # metric_descriptor.value_type = ga_metric.MetricDescriptor.ValueType.INT64 の場合は、"int64_value" である必要がある。（https://cloud.google.com/monitoring/api/ref_v3/rpc/google.monitoring.v3#google.monitoring.v3.TypedValue）
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

    ```

    ```python
    class MonitoringServerConfig:
        # クラス変数
        project_id=os.getenv("PROJECT_ID", "my-project2-303004")
        n_workers=int(os.getenv("N_WORKERS", "1"))
        polling_time=int(os.getenv("POLLING_TIME", "5"))                        # ポーリング間隔時間 (sec単位)
        metric_name=os.getenv("METRIC_NAME", "n_queues_in_redis")               # モニタリング指標名
        metric_resource_type=os.getenv("METRIC_RESOURCE_TYPE", "global")        # モニタリング対象リソースタイプ 
    ```

    ポイントは、以下の通り。

    - Redis のキューに保管されている joib_id のリストを定期的に確認するために、`asyncio `と `concurrent.futures.ProcessPoolExecutor` を使用した並列処理で、無限ループでのポーリング処理を行っている。

    - Python の Cloud Monitoring API を用いた Cloud Monitoring への一連の書き込み処理は、[公式マニュアル](https://cloud.google.com/monitoring/custom-metrics/creating-metrics?hl=ja) にあるコードを参考にしている。大まかな処理の流れは以下の通り<br>
        1. `monitoring_v3.MetricServiceClient()` で、Cloud Monitoring にアクセスするためのクライアントを作成する
        1. `metrics_client.create_metric_descriptor()` で、カスタム指標の記述子（descriptor）を作成する。<br>
            このとき、`metric_descriptor` 引数には、`ga_metric.MetricDescriptor()` で生成したオブジェクト（＝カスタム指標の名前などのプロパティが含まれるオブジェクト）を設定する。<br>
            更に、このオブジェクトのラベルプロパティには、`ga_label.LabelDescriptor()` で生成したオブジェクト（＝カスタム指標のラベル名などのプロパティが含まれるオブジェクト）を設定する。<br>
            尚、`metrics_client.create_metric_descriptor()` でカスタム指標の記述子（descriptor）を作成する際に、すでに同じ名前のカスタム指標が存在するとエラーが出て作成できなくなるので、予め `metrics_client.delete_metric_descriptor()` で同名のカスタム指標を削除しておく。
        1. `metrics_client.create_time_series()` でモニタリング指標に書き込みを行う。<br>
            このとき `time_series` 引数には、`monitoring_v3.TimeSeries()` で作成した `TimeSeries` オブジェクトを設定する。<br>
            更にこの `TimeSeries` オブジェクトの `points` プロパティ `series.points` には、`monitoring_v3.Point()` で作成したカスタム指標の各点（横軸：時間 `"interval"`、縦軸：カスタム指標の値 `"value"`）情報を含んだ `Point` オブジェクトを設定する。このとき、横軸 `"interval"` の値は、`monitoring_v3.TimeInterval()` で生成したオブジェクトを設定する

    - 今回のカスタム指標である Redis のキュー数は、整数値のデータなので、`descriptor.value_type = ga_metric.MetricDescriptor.ValueType.INT64` で整数値をしている。整数値を指定した場合は、`monitoring_v3.Point()` 
    で指定するキー `"value"` の値のキーは `"int64_value"` である必要があることに注意

    - `series.resource.type` で指定可能なカスタム指標でのモニタリング対象リソースタイプとしては、以下のようなものがあるが、ここでは簡単のため `global` を使用している。`global` の場合に設定するラベルは `project_id` のみでよい
        - `global` : 他に適切なリソースタイプがない場合はこのリソースを使用する。（https://cloud.google.com/monitoring/api/resources?hl=ja#tag_global）
        - `generic_node` : ユーザー指定のコンピューティング ノード。
        - `generic_task` : ユーザー定義のタスク。
        - `gce_instance` : Compute Engine のインスタンス
        - `k8s_pod` : Kubernetes ポッド。
        
        > 他にも色々あるが、詳細は、https://cloud.google.com/monitoring/custom-metrics/creating-metrics?hl=ja#global-v-generic を確認のこと


1. docker-compose で API を構成する<br>
    プロキシサーバー・Redis サーバー・バッチサーバー・推論サーバー・モニタリングサーバーを docker-compose で構築する。
    ```yml
    version: '2.3'

    services:
    predict-server:
        container_name: predict-container
        image: predict-server-image
        build:
        context: "api/predict-server/"
        dockerfile: Dockerfile_dev
        volumes:
            - ${PWD}/api/predict-server:/api/predict-server
            - ${PWD}/api/utils:/api/utils
            - ${PWD}/api/config:/api/config
        ports:
            - "5001:5001"
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
        command: bash -c "gunicorn app:app --bind 0.0.0.0:5001 -w 1 -k uvicorn.workers.UvicornWorker --reload"

    redis-server:
        container_name: redis-container
        image: redis:latest
        ports:
            - "6379:6379"
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
        command: bash -c "redis-server"

    batch-server:
        container_name: batch-container
        image: batch-server-image
        build:
            context: "api/batch-server/"
            dockerfile: Dockerfile_dev
        volumes:
            - ${PWD}/api/batch-server:/api/batch-server
            - ${PWD}/api/redis:/api/redis
            - ${PWD}/api/utils:/api/utils
            - ${PWD}/api/config:/api/config
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
        command: bash -c "python batch_server.py"
        depends_on:
            - redis-server
            - predict-server

    proxy-server:
        container_name: proxy-container
        image: proxy-server-image
        build:
            context: "api/proxy-server/"
            dockerfile: Dockerfile_dev
        volumes:
            - ${PWD}/api/proxy-server:/api/proxy-server
            - ${PWD}/api/redis:/api/redis
            - ${PWD}/api/utils:/api/utils
            - ${PWD}/api/config:/api/config
        ports:
            - "5000:5000"
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
        command: bash -c "gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"
        depends_on:
            - redis-server
            - batch-server
            - predict-server

    monitoring-server:
        container_name: monitoring-container
        image: monitoring-server-image
        build:
            context: "api/monitoring-server/"
            dockerfile: Dockerfile_dev
        volumes:
            - ${PWD}/api/monitoring-server:/api/monitoring-server
            - ${PWD}/api/redis:/api/redis
            - ${PWD}/api/config:/api/config
            - ${PWD}/api/key:/api/key
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
            GOOGLE_APPLICATION_CREDENTIALS: "/api/key/cloud-monitoring.json"
        command: bash -c "python monitoring_server.py"
        depends_on:
            - redis-server
            - batch-server
            - predict-server
    ```

    > 作成したサービスアカウントの秘密鍵 (json) は、Cloud Monitoring API を用いて Cloud Monitoring にアクセスするモジュール（今の場合は Monitoring サーバー）に認証させる必要があるが、この処理は、`docker-compose.yml` 内の `environment` タグに `GOOGLE_APPLICATION_CREDENTIALS: "/api/key/cloud-monitoring.json"` を設定して行うようにしている。

1. リクエスト処理のコードを作成する<br>
    `requests` モジュールを用いて、例えば以下のようなリクエスト処理のコードを作成する。<br>
    本項目のコア部分ではないので、詳細は割愛する。

    > リクエスト処理を `curl` コマンドで直接行う場合は、リクエスト処理のコードは不要

1. API を起動する<br>
    ```sh
    $ docker-compose -f docker-compose.yml stop
    $ docker-compose -f docker-compose.yml up -d
    ```

1. リクエスト処理する<br>
    上記作成したリクエスト処理のコードを用いてリクエスト処理する場合は、以下のコマンドを実行する
    ```sh
    $ python request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR}
    ```

<!--
    `curl` コマンドでリクエスト処理する場合は、以下のコマンドを実行する
    ```sh
    # ヘルスチェック
    $ curl http://${HOST}:${PORT}/health
    ```

    ```sh
    # リクエスト処理
    $ IMAGE_BASE64=`base64 in_images/000001_0.jpg`
    $ curl -X POST \
        -H "Content-Type: application/json" \
        -d "{'image': ${IMAGE_BASE64}}" \
        http://${HOST}:${PORT}/start_job
    ```
-->

1. Cloud Monitoring のコンソール画面からメトリックが書き込まれているか確認する<br>
    [Cloud Monitoring コンソール画面の「Metrics Explorer」の項目](https://console.cloud.google.com/monitoring/metrics-explorer?hl=ja&project=my-project2-303004) から、メトリックが書き込まれているか確認する<br>
    <img src="https://user-images.githubusercontent.com/25688193/139066998-01043494-d42f-42cf-9efc-c323498355d4.png" width="1000" /><br>

## ■ 参考サイト
- https://cloud.google.com/monitoring/custom-metrics/creating-metrics?hl=ja
- https://ymotongpoo.hatenablog.com/entry/2019/03/18/085924
