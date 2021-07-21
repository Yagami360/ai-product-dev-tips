# Istio の VirtualSevice のトラフィック分割機能を使用して、Web-API のオンラインA/Bテストを行う

既存の本番環境用の Web-API を新しく作成した Web-API に更新する際に、新しい Web-API をいきなり本番環境で投入すると、Web-API が正しく動かず、最悪公開しているサービスが停止してしまう恐れがある。
そのため、本番環境用の Web-API を更新する際には、A/Bテスト（A:既存のWeb-API, B:新たなWeb-API）を行うのが通例になっている。

シャドウA/Bテストでは、クライアント側に新しい Web-API のレスポンスデータはレスポンスしないため、クライアント側が影響を受けることなく A/Bテストを実施できる一方で、クライアント側にレスポンスデータをレスポンスしないため、クライアント側を含めたシステム全体の A/B テストを実施できないという問題がある。

オンラインA/Bテストでは、クライアント側を含めたシステム全体の A/B テストを実施可能であるが、その一致で、クライアント側がA/Bテストのための処理の変更の影響を受けることになる。

そのため、まずシャドウA/Bテストを行った後に、オンラインA/Bテストを行う形が良い

ここでは、Istio の VirtualService の weight を使用して、既存の Web-API にリクエストを送りつつ、新たな Web-API にもリクエストを行うことで、Web-API のオンラインA/Bテストを実現する方法を記載する

> Web-API のシャドウABテストの方法は、「[Istio の VirtualSevice のトラフィックミラーリング機能を使用して Web-API のシャドウA/Bテストを行う](https://github.com/Yagami360/MachineLearning_Tips/tree/master/ml_ops/41)」を参照のこと

<img src="https://user-images.githubusercontent.com/25688193/126475523-f9c3de9e-08c5-4ee0-bbb6-419c629e344c.png" width="500"><br>

## 方法

1. 推論サーバーのコードを作成する<br>
1. 推論サーバーの Dockerfile を作成する<br>
1. リクエスト処理のコードを作成する<br>

1. k8s のデプロイメント定義ファイルを作成する<br>
    ```yaml
    # 推論サーバー A
    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: predict-pod-a
    spec:
    replicas: 1
    selector:
        matchLabels:
        app: predict-pod
    template:
        metadata:
        labels:                   
            app: predict-pod       
            version: predict-pod-version-a                  # DestinationRule 定義ファイルの spec.subsets.name.labels.version で使用
        annotations:                                        # Istio を使用するためのアノテーション（key: value 形式の metadata）
            sidecar.istio.io/inject: "true"                 # Istio の Envoy（プロキシサーバー）サイドカーの挿入を行うかフラグ
            sidecar.istio.io/proxyCPU: "128m"               # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU 量
            sidecar.istio.io/proxyMemory: "128Mi"           # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU メモリ
            proxy.istio.io/config: "{'concurrency':'1'}"    # Istio の Envoy（プロキシサーバー）サイドカーの並列スレッド数
        spec:
        containers:
        - name: predict-container-a
            image: gcr.io/my-project2-303004/predict-image-gke:latest
            imagePullPolicy: Always
            ports:
            - containerPort: 5000
            name: http-server
            env:
            - name: GRAB_CUT_ITERS
                value: "1"
            command: ["/bin/sh","-c"]
            args: ["gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"]
            resources:
            limits:
                cpu: 500m
                memory: "300Mi"
    ---
    # 推論サーバー B
    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: predict-pod-b
    spec:
    replicas: 1
    selector:
        matchLabels:
        app: predict-pod
    template:
        metadata:
        labels:                   
            app: predict-pod     
            version: predict-pod-version-b                  # DestinationRule 定義ファイルの spec.subsets.name.labels.version で使用  
        annotations:                                        # Istio を使用するためのアノテーション（key: value 形式の metadata）
            sidecar.istio.io/inject: "true"                 # Istio の Envoy（プロキシサーバー）サイドカーの挿入を行うかフラグ
            sidecar.istio.io/proxyCPU: "128m"               # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU 量
            sidecar.istio.io/proxyMemory: "128Mi"           # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU メモリ
            proxy.istio.io/config: "{'concurrency':'1'}"    # Istio の Envoy（プロキシサーバー）サイドカーの並列スレッド数
        spec:
        containers:
        - name: predict-container-b
            image: gcr.io/my-project2-303004/predict-image-gke:latest
            imagePullPolicy: Always
            ports:
            - containerPort: 5000
            name: http-server
            env:
            - name: GRAB_CUT_ITERS
                value: "10"
            command: ["/bin/sh","-c"]
            args: ["gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"]
            resources:
            limits:
                cpu: 500m
                memory: "300Mi"
    ```

    > ２つの推論 Pod `predict-pod-a`, `predict-pod-b` ともに、ポート番号を同じ `5000` にし、サービスも共有する。

    > `template.metadata.annotations` タグに、Istio を使用するためのアノテーション（key: value 形式の metadata）を追加している
    
1. k8s のサービス定義ファイルを作成する<br>
    ```yaml
    # 推論サーバー（推論サーバーAと推論サーバーBで共有）
    apiVersion: v1
    kind: Service
    metadata:
    name: predict-server
    spec:
    type: LoadBalancer
    ports:
        - port: 5000
        targetPort: 5000
        protocol: TCP
    selector:
        app: predict-pod
    ```

    > ２つの推論 Pod `predict-pod-a`, `predict-pod-b` で１つのサービス `predict-server` を共有するようにしている

1. k8s の DestinationRule を作成する<br>
    k8s 内の通信に対して、どのような制限を掛けてあげるかを設定するための定義ファイルである DestinationRule 定義ファイルを作成する
    ```yaml
    # Istio
    apiVersion: networking.istio.io/v1alpha3
    kind: DestinationRule
    metadata:
    name: predict-server
    spec:
    host: predict-server
    trafficPolicy:
        loadBalancer:
        simple: ROUND_ROBIN
    subsets:                            # デプロイメント定義ファイルの `spec.template.metadata.labels.version` タグで定義した値を設定
        - name: predict-pod-subset-a
        labels:
            version: predict-pod-version-a
        - name: predict-pod-subset-b
        labels:
            version: predict-pod-version-b
    ```

    > `spec.subsets` タグに、デプロイメント定義ファイルで指定した２つのプロキシ Pod の `spec.template.metadata.labels.version` タグをそれぞれ指定している

    > `spec.trafficPolicy.connectionPool` タグや `spec.trafficPolicy.outlierDetection` タグで定義可能なサーキットブレーカーの機能はなくしている

1. k8s の VirtualService を作成する<br>
    k8s 内の通信に対して、この通信はこちらの Pod に流し、別の通信は別の Pod に流すといった設定をするための定義ファイルである VirtualService 定義ファイルを作成する。
    今回の主題である新旧 Web-API へのトラフィックの分割を行いたい場合は、この VirtualService の weight 設定で実現できる。

    ```yaml
    # Istio
    apiVersion: networking.istio.io/v1alpha3
    kind: VirtualService
    metadata:
    name: predict-server
    spec:
    hosts:
        - predict-server
    http:
        - route:
            # 推論サーバーA
            - destination:
                host: predict-server
                subset: predict-pod-subset-a      # DestinationRule 定義ファイルの spec.subsets.name タグで定義した値
            weight: 50                          # 50% をサーバーA からのレスポンスにする
            # 推論サーバーB
            - destination:
                host: predict-server
                subset: predict-pod-subset-b      # DestinationRule 定義ファイルの spec.subsets.name タグで定義した値
            weight: 50                          # 50% をサーバーB からのレスポンスにする
    ```

    > `http.route.weight` タグで、それぞれのサーバーへの振り分け確率を設定する。上記の例では、それぞれ weight:50 で設定しているので、サーバーAからのレスポンスとサーバーBからのレスポンスが、半々の確率でクライアント側にレスポンスされる動作になる。

    > ここでは、推論サーバーAと推論サーバーBの weight を 50% の半々の確率にしているが、実際の製品用 Web-API でオンライン A/B テストを実施する際には、まずはサーバーA（99%）、サーバーB（1%）くらいの確率にして、動作に問題なければ、徐々にサーバーBの確率を増やしいくような運用になる。

1. GKE にデプロイする
    ```sh
    $ sh run_gke.sh
    ```

1. GKE 上の API にリクエスト処理する
    ```sh
    $ sh run_gke_request.sh
    ```

    > オンラインABテストなので、新旧 Web-API からのレスポンスデータがレスポンスされる動作になる

1. 新旧 Web-API のログデータを確認する<br>    
    新旧 Web-API のログデータから、両方の Web-API に対してリクエスト処理されていることを確認する

    - 既存の Web-API のログデータ
        ```sh
        $ kubectl exec -it `kubectl get pods | grep "predict-pod-a" | awk '{print $1}' | sed -n 1P` /bin/bash
        $ cat app.log
        ```
        ```sh
        [app] time 10:41:48 | 推論サーバーを起動しました
        2021-07-21 10:42:41 INFO _health START args=() kwds={}
        2021-07-21 10:42:41 INFO _health END elapsed_time [ms]=0.47660, return {'health': 'ok'}
        2021-07-21 10:42:42 INFO predict START job_id=82393d
        2021-07-21 10:42:43 INFO predict END job_id=82393d, elapsed_time [ms]=1063.08198
        2021-07-21 10:42:43 INFO predict START job_id=ba43dd
        2021-07-21 10:42:44 INFO predict END job_id=ba43dd, elapsed_time [ms]=713.55724
        2021-07-21 10:42:44 INFO predict START job_id=d26101
        2021-07-21 10:42:45 INFO predict END job_id=d26101, elapsed_time [ms]=971.81535
        2021-07-21 10:42:45 INFO predict START job_id=cba977
        2021-07-21 10:42:46 INFO predict END job_id=cba977, elapsed_time [ms]=772.17650
        ```

    - 新しい Web-API のログデータ
        ```sh
        $ kubectl exec -it `kubectl get pods | grep "predict-pod-b" | awk '{print $1}' | sed -n 1P` /bin/bash
        $ cat app.log
        ```
        ```sh
        [app] time 10:41:48 | 推論サーバーを起動しました
        2021-07-21 10:42:41 INFO _health START args=() kwds={}
        2021-07-21 10:42:41 INFO _health END elapsed_time [ms]=0.32949, return {'health': 'ok'}
        2021-07-21 10:42:47 INFO predict START job_id=9ce485
        2021-07-21 10:42:48 INFO predict END job_id=9ce485, elapsed_time [ms]=1613.63125
        ```
    
## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter6_operation_management/online_ab_pattern

