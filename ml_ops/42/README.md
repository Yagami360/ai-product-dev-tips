# Istio の VirtualSevice のトラフィック分割機能を使用して、Web-API のオンラインA/Bテストを行う

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
    今回の主題である新旧 Web-API へのトラフィックの分割を行いたい場合は、この VirtualService の設定で実現できる。

    ```yaml
    ```

    > xxx
    
1. GKE にデプロイする
    ```sh
    $ sh run_gke.sh
    ```

1. GKE 上の API にリクエスト処理する
    ```sh
    $ sh run_gke_request.sh
    ```

    > オンラインABテストなので、新旧 Web-API からのレスポンスデータがレスポンスされる動作になる


## ■ 参考サイト
- 

