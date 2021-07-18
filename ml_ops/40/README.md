# Istio の VirtualSevice を使用してリクエストデータのヘッダーに応じて異なる Web-API で推論する

機械学習モデルにおいては、ある学習用データをある特定のドメイン（日本人、外国人など）に特化させることで、そのドメイン内での推論品質を向上させることよく行われることである。

ここでは、機械学習 API において、このようなドメイン特化したモデルが複数存在する場合に、クライアント側から送信されるリクエストヘッダーに応じて、Istio の VirtualSevice を用いて、
適切な機械学習モデルで推論するシステムを構築する

> 入力データのドメインに応じて、異なる機械学習モデルの API で推論すること自体は、Istio の VirtualSevice を用いなくとも実現可能であることに注意

<img src="https://user-images.githubusercontent.com/25688193/126056972-1b1d9136-1237-43df-856c-0035f8c8f3ce.png" width="500"><br>

## ■ 方法

1. プロキシサーバーのコードを作成する<br>
1. プロキシサーバーの Dockerfile を作成する<br>
1. 推論サーバーのコードを作成する<br>
1. 推論サーバーの Dockerfile を作成する<br>

1. k8s のデプロイメント定義ファイルを作成する<br>
    ```yaml
    # proxy Pod1
    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: proxy-pod1
    spec:
    replicas: 1
    selector:
        matchLabels:
        app: proxy-pod
    template:
        metadata:
        labels:                   
            app: proxy-pod       
            version: proxy-pod-version1                     #
        annotations:                                      # Istio を使用するためのアノテーション（key: value 形式の metadata）
            sidecar.istio.io/inject: "true"                 # Istio の Envoy（プロキシサーバー）サイドカーの挿入を行うかフラグ
            sidecar.istio.io/proxyCPU: "128m"               # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU 量
            sidecar.istio.io/proxyMemory: "128Mi"           # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU メモリ
            proxy.istio.io/config: "{'concurrency':'1'}"    # Istio の Envoy（プロキシサーバー）サイドカーの並列スレッド数
        spec:
        containers:
        - name: proxy-container1
            image: gcr.io/my-project2-303004/proxy-image-gke:latest
            imagePullPolicy: Always
            ports:
            - containerPort: 5000
            name: http-server
            env:
            - name: PREDICT_SERVER_URL
                value: "http://predict-server1:5010"
            command: ["/bin/sh","-c"]
            args: ["gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"]
            resources:
            limits:
                cpu: 500m
                memory: "300Mi"
    ---
    # proxy Pod2
    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: proxy-pod2
    spec:
    replicas: 1
    selector:
        matchLabels:
        app: proxy-pod
    template:
        metadata:
        labels:                   
            app: proxy-pod       
            version: proxy-pod-version2                                    #
        annotations:                                      # Istio を使用するためのアノテーション（key: value 形式の metadata）
            sidecar.istio.io/inject: "true"                 # Istio の Envoy（プロキシサーバー）サイドカーの挿入を行うかフラグ
            sidecar.istio.io/proxyCPU: "128m"               # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU 量
            sidecar.istio.io/proxyMemory: "128Mi"           # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU メモリ
            proxy.istio.io/config: "{'concurrency':'1'}"    # Istio の Envoy（プロキシサーバー）サイドカーの並列スレッド数
        spec:
        containers:
        - name: proxy-container2
            image: gcr.io/my-project2-303004/proxy-image-gke:latest
            imagePullPolicy: Always
            ports:
            - containerPort: 5000
            name: http-server
            env:
            - name: PREDICT_SERVER_URL
                value: "http://predict-server2:5011"
            command: ["/bin/sh","-c"]
            args: ["gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"]
            resources:
            limits:
                cpu: 500m
                memory: "300Mi"
    ---
    # 推論サーバー１
    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: predict-pod1
    spec:
    replicas: 1
    selector:
        matchLabels:
        app: predict-pod1
    template:
        metadata:
        labels:                   
            app: predict-pod1       
        annotations:                                      # Istio を使用するためのアノテーション（key: value 形式の metadata）
            sidecar.istio.io/inject: "true"                 # Istio の Envoy（プロキシサーバー）サイドカーの挿入を行うかフラグ
            sidecar.istio.io/proxyCPU: "128m"               # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU 量
            sidecar.istio.io/proxyMemory: "128Mi"           # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU メモリ
            proxy.istio.io/config: "{'concurrency':'1'}"    # Istio の Envoy（プロキシサーバー）サイドカーの並列スレッド数
        spec:
        containers:
        - name: predict-container1
            image: gcr.io/my-project2-303004/predict-image-gke:latest
            imagePullPolicy: Always
            ports:
            - containerPort: 5010
            name: http-server
            env:
            - name: GRAB_CUT_ITERS
                value: "1"
            command: ["/bin/sh","-c"]
            args: ["gunicorn app:app --bind 0.0.0.0:5010 -w 1 -k uvicorn.workers.UvicornWorker --reload"]
            resources:
            limits:
                cpu: 500m
                memory: "300Mi"
    ---
    # 推論サーバー２
    apiVersion: apps/v1
    kind: Deployment
    metadata:
    name: predict-pod2
    spec:
    replicas: 1
    selector:
        matchLabels:
        app: predict-pod2
    template:
        metadata:
        labels:                   
            app: predict-pod2       
        annotations:                                      # Istio を使用するためのアノテーション（key: value 形式の metadata）
            sidecar.istio.io/inject: "true"                 # Istio の Envoy（プロキシサーバー）サイドカーの挿入を行うかフラグ
            sidecar.istio.io/proxyCPU: "128m"               # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU 量
            sidecar.istio.io/proxyMemory: "128Mi"           # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU メモリ
            proxy.istio.io/config: "{'concurrency':'1'}"    # Istio の Envoy（プロキシサーバー）サイドカーの並列スレッド数
        spec:
        containers:
        - name: predict-container2
            image: gcr.io/my-project2-303004/predict-image-gke:latest
            imagePullPolicy: Always
            ports:
            - containerPort: 5011
            name: http-server
            env:
            - name: GRAB_CUT_ITERS
                value: "10"
            command: ["/bin/sh","-c"]
            args: ["gunicorn app:app --bind 0.0.0.0:5011 -w 1 -k uvicorn.workers.UvicornWorker --reload"]
            resources:
            limits:
                cpu: 500m
                memory: "300Mi"
    ```

    > ２つのプロキシ Pod `proxy-pod1`, `proxy-pod２` ともに、ポート番号を同じ `5000` にし、サービスも共有する。

    > `template.metadata.annotations` タグに、Istio を使用するためのアノテーション（key: value 形式の metadata）を追加している

1. k8s のサービス定義ファイルを作成する<br>
    ```yaml
    # プロキシサーバー
    apiVersion: v1
    kind: Service
    metadata:
    name: proxy-server
    spec:
    type: LoadBalancer
    ports:
        - port: 5000
        targetPort: 5000
        protocol: TCP
    selector:
        app: proxy-pod  # デプロイメント定義ファイルで定義した Pod の識別名。app:sample-pod のラベルがつけられた Pod を通信先とする
    ---
    # 推論サーバー1
    apiVersion: v1
    kind: Service
    metadata:
    name: predict-server1
    spec:
    type: LoadBalancer
    ports:
        - port: 5010
        targetPort: 5010
        protocol: TCP
    selector:
        app: predict-pod1
    ---
    # 推論サーバー2
    apiVersion: v1
    kind: Service
    metadata:
    name: predict-server2
    spec:
    type: LoadBalancer
    ports:
        - port: 5011
        targetPort: 5011
        protocol: TCP
    selector:
        app: predict-pod2
    ```

    > ２つのプロキシ Pod `proxy-pod1`, `proxy-pod２` で１つのサービス `proxy-server` を共有するようにしている

1. k8s の DestinationRule を作成する<br>
    k8s 内の通信に対して、どのような制限を掛けてあげるかを設定するための定義ファイルである DestinationRule 定義ファイルを作成する
    ```yaml
    # Istio
    apiVersion: networking.istio.io/v1alpha3
    kind: DestinationRule
    metadata:
    name: proxy-server
    spec:
    host: proxy-server
    trafficPolicy:
        loadBalancer:
        simple: ROUND_ROBIN
    subsets:                            # デプロイメント定義ファイルの `spec.template.metadata.labels.version` タグで定義した値を設定
        - name: proxy-pod-subset1
        labels:
            version: proxy-pod-version1
        - name: proxy-pod-subset2
        labels:
            version: proxy-pod-version2
    ```

    > `spec.subsets` タグに、デプロイメント定義ファイルで指定した２つのプロキシ Pod の `spec.template.metadata.labels.version` タグをそれぞれ指定している

    > `spec.trafficPolicy.connectionPool` タグや `spec.trafficPolicy.outlierDetection` タグで定義可能なサーキットブレーカーの機能はなくしている

1. k8s の VirtualService を作成する<br>
    k8s 内の通信に対して、この通信はこちらの Pod に流し、別の通信は別の Pod に流すといった設定をするための定義ファイルである VirtualService 定義ファイルを作成する。
    今回の主題であるクライアント側で設定したリクエストヘッダーの値に応じて、リクエスト送信先のプロキシサーバーを切り替えたい場合は、この VirtualService の設定で実現できる。

    ```yaml
    # Istio
    apiVersion: networking.istio.io/v1alpha3
    kind: VirtualService
    metadata:
    name: proxy-server
    spec:
    hosts:
      - proxy-server
    http:
      - match:                          # `http.match` タグで、リクエスト送信先の振り分け条件を定義できる
        - headers:                      # リクエストヘッダー
            target:
              exact: condition1         # ヘッダー値
        route:                          # `http.match.route` タグで、`match` タグで定義した振り分け条件に一致したときのリクエスト送信先を定義できる
        - destination:
            host: proxy-server
            subset: proxy-pod-subset1   # DestinationRule 定義ファイルの spec.subsets.name タグで定義した値
        timeout: 10s
      - route:                          # 最後に定義した `http.route` タグで、`match` タグで定義した振り分け条件に一致しない場合のリクエスト送信先を定義できる。
        - destination:
            host: proxy-server
            subset: proxy-pod-subset2
        timeout: 10s
    ```

    今回の場合は、リクエストヘッダーの `"target"` の値が `"condition1"` だった場合、１つの目のプロキシサーバーにリクエスト処理し、`"condition1"` 以外だった場合、２つの目のプロキシサーバーにリクエスト処理される動作になる。

    > `http.match` タグで、リクエスト送信先の振り分け条件を定義できる

    > `http.match.route` タグで、`match` タグで定義した振り分け条件に一致したときのリクエスト送信先を定義できる

    > 最後に定義した `http.route` タグで、`match` タグで定義した振り分け条件に一致しない場合のリクエスト送信先を定義できる。


1. リクエスト処理のコードを作成する
    ```python
    ```

    > API でリクエストヘッダーの `"target"` の値が `"condition1"` だった場合、１つの目のプロキシサーバーにリクエスト処理し、`"condition1"` 以外だった場合、２つの目のプロキシサーバーにリクエスト処理される動作にしているので、`requests.post()` の `headers` 引数に `headers = { "Content-Type": "application/json", "target": "condition1",}` を設定している

1. GKE にデプロイする
    ```sh
    $ sh run_gke.sh
    ```

1. GKE 上の API にリクエスト処理する
    ```sh
    $ sh run_gke_request.sh
    ```


## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter6_operation_management/condition_based_pattern
- http://blog.1q77.com/2020/03/istio-part3/#toc5