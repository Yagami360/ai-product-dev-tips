# 【GKE】Cloud Monitoring でのカスタム指標を k8s の外部メトリックとしてオートスケールする

k8s では、以下の２種類の独自のメトリックに基づくオートスケール機能が提供されている。<br>

- カスタムメトリクス（＝カスタム指標）でのオートスケール機能<br>
    Pod やその他 k8s リソースに紐づくリソースでのオートスケール機能

- 外部メトリクス（＝外部指標）でのオートスケール機能<br>
    k8s リソースに紐づかないリソースでのオートスケール機能

ここでは、Cloud Monitoring でのカスタム指標を外部メトリクス（＝外部指標）として採用し、k8s の外部指標でのオートスケール機能を使用したオートスケール方法について記載する

> ここでいう「k8s のカスタム指標」と「Cloud Monitoring のカスタム指標」は同じではなく、「k8s の外部指標」と「loud Monitoring のカスタム指標」が一致することに注意

<img src="https://user-images.githubusercontent.com/25688193/139519339-ddfa99fd-f18b-4851-81bc-fa36009db76f.png" width="1000"><br>

より詳細には、上図のように、「プロキシサーバ・バッチサーバ・モニタリングサーバー・外部メトリクスサーバー・Redis サーバー・推論サーバー」から構成される GKE 上の非同期 API において、Redis に保存されている job_id のキュー数を Cloud Monitoring への書き込み、この Cloud Monitoring に書き込まれたカスタム指標（＝Redisのキュー数）に基づき、k8s の外部指標でのオートスケール機能を利用してオートスケールを行う

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

    ここで、作成したサービスアカウントの秘密鍵 (json) は、Cloud Monitoring API を用いて Cloud Monitoring にアクセスするモジュール（今の場合は Monitoring サーバー）に認証させる必要があるが、この処理は、k8s マニフェストファイル `k8s/monitoring.ym` 内の `env` タグに `GOOGLE_APPLICATION_CREDENTIALS: "/api/key/cloud-monitoring.json"` を設定して行うようにしている。

    > モニタリングサーバーの起動スクリプトや初期化スクリプトで、`export GOOGLE_APPLICATION_CREDENTIALS = "json鍵へのパス"` を追加する形式でもよい

    - `k8s/monitoring.yml`
        ```yaml
        # Pod
        apiVersion: apps/v1
        kind: Deployment
        metadata:
        name: monitoring-pod
        labels:
            app: monitoring-pod
        spec:
        replicas: 1
        selector:
            matchLabels:
            app: monitoring-pod
        template:
            metadata:
            labels:
                app: monitoring-pod
            spec:
            containers:
            - name: monitoring-container
                image: gcr.io/my-project2-303004/monitoring-image-gke:latest
                env:
                - name: GOOGLE_APPLICATION_CREDENTIALS          # 作成したサービスアカウントの秘密鍵 (json) を環境変数 GOOGLE_APPLICATION_CREDENTIALS に適用
                    value: /api/key/cloud-monitoring.json       # 
                - name: POLLING_TIME
                    value: "1"
                - name: DEBUG
                    value: "True"
                command: ["/bin/sh","-c"]
                args: ["python monitoring_server.py"]
        ```

1. redis サーバーのコード [api/redis/redis_client.py](https://github.com/Yagami360/MachineLearning_Tips/blob/master/ml_ops/50/api/redis/redis_client.py) を作成する<br>
    Redis の Python API を用いて Redis サーバーに接続するためのコードを作成する。<br>
    本項目のコア部分ではないので、詳細は割愛する。

1. プロキシサーバーのコード [api/proxy-server/app.py](https://github.com/Yagami360/MachineLearning_Tips/blob/master/ml_ops/50/api/proxy-server/app.py)  を作成する<br>
    プロキシサーバでは、FastAPI を用いて、推論リクエストをジョブIDとして定義し、Redis のキューにジョブIDを push している。<br>
    本項目のコア部分ではないので、詳細は割愛する。

1. バッチサーバーのコード [api/batch-server/batch_server.py](https://github.com/Yagami360/MachineLearning_Tips/blob/master/ml_ops/50/api/batch-server/batch_server.py)  を作成する<br>
    バッチサーバーでは、Redis のデータを定期的にポーリングし、データがあれば推論サーバーにリクエスト処理する。その後、推論サーバーからのレスポンスデータを Redis に保存する。<br>
    バッチサーバーでのポーリング処理は、`asyncio` と `concurrent.futures.ProcessPoolExecutor` を使用した並列処理で行っている<br>
    本項目のコア部分ではないので、詳細は割愛する。

1. 推論サーバーのコード [api/predict-server/app.py](https://github.com/Yagami360/MachineLearning_Tips/blob/master/ml_ops/50/api/predict-server/app.py) を作成する<br>
    ここでは例えば、OpenCV の `cv2.grabCut()` を用いた推論サーバーを構築する。機械学習 API の場合は、この推論サーバーの部分が機械学習モデルを使用した推論処理になる。<br>
    本項目のコア部分ではないので、詳細は割愛する。

1. モニタリングサーバーのコード [api/monitoring-server/monitoring_server.py](https://github.com/Yagami360/MachineLearning_Tips/blob/master/ml_ops/50/api/monitoring-server/monitoring_server.py) を作成する<br>
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

        # 指標記述子
        descriptor = ga_metric.MetricDescriptor()
        descriptor.type = "custom.googleapis.com/" + MonitoringServerConfig.metric_name         # 使用できるプレフィックスは custom.googleapis.com/ と external.googleapis.com/prometheus 
        descriptor.metric_kind = ga_metric.MetricDescriptor.MetricKind.GAUGE                    #
        descriptor.value_type = ga_metric.MetricDescriptor.ValueType.INT64                      #
        descriptor.description = "job_ids in redis queue."

        # descriptor.labels に設定するラベル
        labels = ga_label.LabelDescriptor()
        labels.key = MonitoringServerConfig.metric_name + "_label"
        labels.value_type = ga_label.LabelDescriptor.ValueType.STRING
        labels.description = "label for " + MonitoringServerConfig.metric_name
        descriptor.labels.append(labels)

        # 
        descriptor = metrics_client.create_metric_descriptor(name= "projects/" + MonitoringServerConfig.project_id, metric_descriptor=descriptor)
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


1. k8s のマニフェストファイルを作成する<br>
    プロキシサーバー・Redis サーバー・バッチサーバー・推論サーバー・モニタリングサーバーのマニフェストファイルを作成する。

    - プロキシサーバーのマニフェストファイル<br>
        本項目のコア部分ではないので、詳細は割愛する。

    - バッチサーバーのマニフェストファイル<br>
        本項目のコア部分ではないので、詳細は割愛する。

    - Redis サーバーのマニフェストファイル<br>
        本項目のコア部分ではないので、詳細は割愛する。

    - モニタリングサーバーのマニフェストファイル<br>
        ```yml
        # Pod
        apiVersion: apps/v1
        kind: Deployment
        metadata:
        name: monitoring-pod
        labels:
            app: monitoring-pod
        spec:
        replicas: 1
        selector:
            matchLabels:
            app: monitoring-pod
        template:
            metadata:
            labels:
                app: monitoring-pod
            spec:
            containers:
            - name: monitoring-container
                image: gcr.io/my-project2-303004/monitoring-image-gke:latest
                env:
                - name: GOOGLE_APPLICATION_CREDENTIALS
                    value: /api/key/cloud-monitoring.json
                - name: POLLING_TIME
                    value: "1"
                - name: DEBUG
                    value: "True"
                command: ["/bin/sh","-c"]
                args: ["python monitoring_server.py"]
        ```

        ポイントは、以下の通り

        - 作成したサービスアカウントの秘密鍵 (json) は、Cloud Monitoring API を用いて Cloud Monitoring にアクセスするモジュール（今の場合は Monitoring サーバー）に認証させる必要があるが、この処理は、各種 k8s マニフェストファイル内の `env` タグに `GOOGLE_APPLICATION_CREDENTIALS: "/api/key/cloud-monitoring.json"` を設定して行うようにしている。

        - モニタリングサーバーはオートスケールを行う必要はないので、`HorizontalPodAutoscaler` リソースを定義していない

    - 推論サーバーのマニフェストファイル<br>
        ```yml
        ---
        # Pod
        apiVersion: apps/v1
        kind: Deployment
        metadata:
        name: predict-pod
        labels:
            app: predict-pod
        spec:
        replicas: 1
        selector:
            matchLabels:
            app: predict-pod
        template:
            metadata:
            labels:
                app: predict-pod
            spec:
            containers:
            - name: predict-container
                image: gcr.io/my-project2-303004/predict-image-gke:latest
                command: ["/bin/sh","-c"]
                args: ["gunicorn app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5001 --workers 1 --threads 1 --backlog 256 --reload"]
        ---
        # Service
        apiVersion: v1
        kind: Service
        metadata:
        name: predict-server
        spec:
        type: LoadBalancer
        ports:
            - port: 5001
            targetPort: 5001
            protocol: TCP
        selector:
            app: predict-pod
        ---
        # HorizontalPodAutoscaler
        apiVersion: autoscaling/v2beta1
        kind: HorizontalPodAutoscaler
        metadata:
        name: predict-auto-scale
        namespace: default
        spec:
        scaleTargetRef:     # autoscale 対象となる `scaled resource object` を指定
            apiVersion: apps/v1
            kind: Deployment
            name: predict-pod
        minReplicas: 1      # 最小 Pod 数
        maxReplicas: 4      # 最大 Pod 数
        metrics:
        - type: External  # 外部メトリクス（kubernetesクラスタ内のリソースとは関係しないメトリクス）
            external:
            metricName: custom.googleapis.com|n_queues_in_redis   # Kubernetes API では指標名にスラッシュを使用できないため、パイプ記号（|）で置き換える必要がある
            targetValue: 0.5                                      # 1つのPodが処理すべき値を決め打ちで指定する。
        ```

        ポイントは、以下の通り

        - 推論サーバーはオートスケール対象なのでので、水平 Pod オートスケールを行うための `HorizontalPodAutoscaler` リソースを定義している。

        - この `HorizontalPodAutoscaler` リソースに対して、`metrics.type: External` で外部メトリック（＝外部指標）をオートスケール指標とするように定義している。そして、具体的な外部指標名 `metrics.metricName` には、Cloud Monitoring に書き込んでいるカスタム指標（＝Redisの joib_id のキュー数） `custom.googleapis.com|n_queues_in_redis` を設定している

            > k8s には外部指標でのオートスケール機能とカスタム指標でのオートスケール機能があるが、ここでいう「k8s のカスタム指標」と「Cloud Monitoring のカスタム指標」は同じではなく、「k8s の外部指標」と「loud Monitoring のカスタム指標」が一致することに注意

        - このとき、Kubernetes API では指標名にスラッシュ(`/`)を使用できないため、パイプ記号（`|`）で置き換える必要があることに注意。また、ここで設定する外部指標名（＝Cloud Monitoring でのカスタム指標名）としては、`n_queues_in_redis` 単体や `projects|my-project2-303004|metricDescriptors|custom.googleapis.com|n_queues_in_redis` ではなく、`custom.googleapis.com|n_queues_in_redis` となることに注意

        - オートスケールのしきい値は、`targetAverageValue` ではなく `targetValue` で定義している。
            - `targetValue` : 1つのPodに対してのしきい値
            - `targetAverageValue` : 外部指標全体の数値をPod数で割ったときのしきい値。例えば Pod 数（５）・外部指標値（100）・targetAverageValue=10の場合は、 外部指標値/Pod 数=20 になって、targetAverageValue=10 を超えているので水平オートスケールが行われる

        - この `metrics.type: External` を定義しただけでは、例え、Cloud Monitoring に対応するカスタム指標を書き込んでいたとしても、実際にオートスケールは行われないことに注意。この外部指標でオートスケール出来るようにするためには、後述の Stackdriver Adapter を GKE クラスタにデプロイして、`custom-metrics-stackdriver-adapter` という名前の外部メトリックサーバーの Pod を起動させておく必要がある

1. docker image を Container Registry にアップロードするための `cloudbuild.yml` を作成する<br>
    本項目のコア部分ではないので、詳細は割愛する。

1. docker image を Container Registry にアップロードする<br>
    ```sh
    $ gcloud builds submit --config cloudbuild.yml --timeout 3600
    ```

1. GKE クラスタを作成する<br>
    ```sh
    # GKE クラスタを作成する
    $ gcloud container clusters create ${CLUSTER_NAME} \
        --region ${ZONE} \
        --num-nodes 1 \
        --machine-type ${CPU_TYPE} \
        --disk-size ${DISK_SIZE} \
        --scopes=gke-default,logging-write

    # 作成したクラスタに切り替える
    gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${ZONE} --project ${PROJECT_ID}
    ```

1. GKE クラスタに Stackdriver Adapter をデプロイする<br>
    GKE クラスタにカスタム指標のためのアダプタである Stackdriver Adapter をデプロイする。この際の Stackdriver Adapter の k8s マニフェストファイルは、GCP側で予め用意されているマニフェストファイルを使用する。<br>
    このデプロイ処理を行うことで、`custom-metrics-stackdriver-adapter` という名前の外部メトリックサーバーの Pod が起動し、k8s マニフェスファイルトの `HorizontalPodAutoscaler` リソース内で `spec.metrics.type: External` で定義した Cloud Monitoring からのカスタム指標 `spec.metrics.external.metricName: custom.googleapis.com|${カスタム指標名}` で水平 Pod オートスケールが行えるようになる。
    ```sh
    $ kubectl create clusterrolebinding cluster-admin-binding --clusterrole cluster-admin --user "$(gcloud config get-value account)"
    $ kubectl create -f https://raw.githubusercontent.com/GoogleCloudPlatform/k8s-stackdriver/master/custom-metrics-stackdriver-adapter/deploy/production/adapter.yaml
    ```

1. GKE クラスタに各種 k8s リソースをデプロイする<br>
    ```sh
    $ kubectl apply -f k8s/redis.yml
    $ kubectl apply -f k8s/predict.yml
    $ kubectl apply -f k8s/proxy.yml
    $ kubectl apply -f k8s/batch.yml
    $ kubectl apply -f k8s/monitoring.yml
    ```

1. リクエスト処理のコードを作成する<br>
    `requests` モジュールを用いて、例えば以下のようなリクエスト処理のコードを作成する。<br>
    本項目のコア部分ではないので、詳細は割愛する。

    > リクエスト処理を `curl` コマンドで直接行う場合は、リクエスト処理のコードは不要

1. リクエスト処理する<br>
    上記作成したリクエスト処理のコードを用いてリクエスト処理する場合は、以下のコマンドを実行する
    ```sh
    $ SERVICE_NAME=proxy-server
    $ HOST=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`
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


1. 推論サーバーがオートスケールされていることを確認する<br>
    ```sh
    $ watch kubectl get HorizontalPodAutoscaler
    ```

## ■ 参考サイト
- https://cloud.google.com/monitoring/custom-metrics/creating-metrics?hl=ja
- https://cloud.google.com/kubernetes-engine/docs/tutorials/external-metrics-autoscaling
- https://open-groove.net/aws-eks/k8s-hpa-targetvalue/