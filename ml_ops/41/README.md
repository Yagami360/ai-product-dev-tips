# Istio の VirtualSevice のトラフィックミラーリング機能を使用して Web-API のシャドウA/Bテストを行う

既存の本番環境用の Web-API を新しく作成した Web-API に更新する際に、新しい Web-API をいきなり本番環境で投入すると、Web-API が正しく動かず、最悪公開しているサービスが停止してしまう恐れがある。

そのため、本番環境用の Web-API を更新する際には、A/Bテスト（A:既存のWeb-API, B:新たなWeb-API）を行うのが通例になっている。
特に、シャドウA/Bテストでは、クライアント側に新しい Web-API のレスポンスデータはレスポンスしないため、クライアント側が影響を受けることなく A/Bテストを実施できる。これにより、公開しているサービスへの悪影響をなくすことができる。一方で、クライアント側にレスポンスデータをレスポンスしないため、クライアント側を含めたシステム全体の A/B テストを実施できないというデメリットはある。

シャドウABテストの場合の新旧 Web-API の動作確認は、それぞれの Web-API のログデータなどから確認できる

> システム全体の A/B テストを実施するには、オンライン A/B テストを行えばよい。まずはシャドウA/Bテストで Web-API 単体の A/B テストを行い、その後オンライン A/B テストでシステム全体の A/B テストを行う流れがベスト

ここでは、Istio の VirtualService のミラーリング機能（＝複数のエンドポイントにトラフィックをミラーリングする機能）を使用して、既存の Web-API にリクエストを送りつつ、新たな Web-API にもリクエストを行うことで、Web-API のシャドウA/Bテストを実現する方法を記載する

<img src="https://user-images.githubusercontent.com/25688193/126057460-c17f1710-bca0-4128-aa61-d6cf22ffbd00.png" width="500"><br>

## ■ 方法

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
        annotations:                                      # Istio を使用するためのアノテーション（key: value 形式の metadata）
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
        annotations:                                      # Istio を使用するためのアノテーション（key: value 形式の metadata）
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
    今回の主題であるミラーリング機能（＝既存の Web-API にリクエストを送りつつ新たな Web-API にもリクエストを行う）を使用したい場合は、この VirtualService の設定で実現できる。

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
            - destination:
                host: predict-server
                subset: predict-pod-subset-a      # DestinationRule 定義ファイルの spec.subsets.name タグで定義した値
            weight: 100
        # ミラーリングを行うリクエスト先  
        mirror:
            host: predict-server
            subset: predict-pod-subset-b          # DestinationRule 定義ファイルの spec.subsets.name タグで定義した値
        mirror_percent: 100                     # ミラーリングを行う割合
    ```

    > `spec.http.route.mirror` タグで、ミラーリングを行うリクエスト先（＝今の場合新しい Web-API）を設定している

1. GKE にデプロイする
    ```sh
    $ sh run_gke.sh
    ```

1. GKE 上の API にリクエスト処理する
    ```sh
    $ sh run_gke_request.sh
    ```

    > シャドウABテストなので、従来の Web-API からのレスポンスデータのみレスポンスされる動作になる

1. 新旧 Web-API のログデータを確認する<br>    
    新旧 Web-API のログデータから、両方の Web-API に対してリクエスト処理されていることを確認する

    - 既存の Web-API のログデータ
        ```sh
        $ kubectl exec -it `kubectl get pods | grep "predict-pod-a" | awk '{print $1}' | sed -n 1P` /bin/bash
        $ cat app.log
        ```
        ```sh
        [app] time 06:09:56 | 推論サーバーを起動しました
        2021-07-18 06:10:31 INFO _health START args=() kwds={}
        2021-07-18 06:10:31 INFO _health END elapsed_time [ms]=0.39196, return {'health': 'ok'}
        2021-07-18 06:10:31 INFO predict START job_id=c47247
        2021-07-18 06:10:32 INFO predict END job_id=c47247, elapsed_time [ms]=1146.03829
        2021-07-18 06:10:34 INFO predict START job_id=45f365
        2021-07-18 06:10:35 INFO predict END job_id=45f365, elapsed_time [ms]=1345.09301
        ```

    - 新しい Web-API のログデータ
        ```sh
        $ kubectl exec -it `kubectl get pods | grep "predict-pod-b" | awk '{print $1}' | sed -n 1P` /bin/bash
        $ cat app.log
        ```
        ```sh
        [app] time 06:09:56 | 推論サーバーを起動しました
        2021-07-18 06:10:30 INFO _health START args=() kwds={}
        2021-07-18 06:10:30 INFO _health END elapsed_time [ms]=0.33045, return {'health': 'ok'}
        2021-07-18 06:10:32 INFO predict START job_id=adaf2d
        2021-07-18 06:10:34 INFO predict END job_id=adaf2d, elapsed_time [ms]=1538.02419
        2021-07-18 06:10:36 INFO predict START job_id=348c55
        2021-07-18 06:10:37 INFO predict END job_id=348c55, elapsed_time [ms]=1556.45537
        2021-07-18 06:10:38 INFO predict START job_id=0d63c6
        2021-07-18 06:10:39 INFO predict END job_id=0d63c6, elapsed_time [ms]=1884.23991
        ```

## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter6_operation_management/shadow_ab_pattern
