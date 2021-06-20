# 【GKE】GKE で構成した Web API に Istio を使用したサーキットブレーカーを導入する

「[GKE で構成した Web API に vegeta atteck を使用して負荷テストする](https://github.com/Yagami360/MachineLearning_Tips/tree/master/ml_ops/25)」構築した GKE 上の Web-API に、短時間で多量のリクエスト処理が来た場合に、プロキシサーバー側でわざとリクエスト処理の一部を遮断するサーキットブレーカーの仕組みを導入する

ここでは、Istio を使用したサーキットブレーカーの仕組みを導入する

> - Istio<br>
>   k8s において、サービス間の通信をサポートするための各種機能をもつアドオンツール<br>
>   Istio に機能の１つに、Istio サイドカーコンテナ（＝同じ Pod 内のコンテナとディスクを共有するコンテナ）として動作する Envoy という名前のプロキシを k8s クラスタに導入することで、k8s クラスタ内部と外部の通信を制御する機能があり、この通信管理機能の中にサーキットブレーカーの機能が用意されている。ここでは、この機能を利用してサーキットブレーカーの仕組みを GKE 上の Web-API に導入する

## 手順

1. API の構成<br>
    1. API のコードを作成する<br>
        ここでは、簡単のため FastAPI を使用した以下のような API コードを作成する
        ```python
        from fastapi import FastAPI

        app = FastAPI()

        users_db = {
            "name" : {
                0 : "user1",
                1 : "user2",
                2 : "user3",
            },
            "age" : {
                0 : "24",
                1 : "30",
                2 : "18",
            },
        }

        #======================================
        # GET method
        #======================================
        @app.get("/")
        def root():
            return 'Hello Flask-API Server!\n'

        @app.get("/health")
        def health():
            return {"health": "ok"}

        @app.get("/metadata")
        def metadata():
            return users_db

        @app.get("/users_name/{users_id}")
        def get_user_name_by_path_parameter(
            users_id: int,  # パスパラメーター
        ):
            return users_db["name"][users_id]

        @app.get("/users_name/")
        def get_user_name_by_query_parameter(
            users_id: int, # クエリパラメーター
        ):
            return users_db["name"][users_id]

        @app.get("/users/{attribute}")
        def get_user_by_path_and_query_parameter(
            attribute: str, # パスパラメーター
            users_id: int,  # クエリパラメーター
        ):
            return users_db[attribute][users_id]

        #======================================
        # POST method
        #======================================
        from pydantic import BaseModel
        # `pydantic.BaseModel` 継承クラスでリクエストボディを定義
        class UserData(BaseModel):
            id: int
            name: str
            age: str

        @app.post("/add_users/")
        def add_user(
            user_data: UserData,     # リクエストボディ
        ):
            users_db["name"][user_data.id] = user_data.name
            users_db["age"][user_data.id] = user_data.age
            return users_db
        ```

    1. GKE にデプロイする docker image ための Dockerfile を作成する<br>
        ```dockerfile
        #-----------------------------
        # Docker イメージのベースイメージ
        #-----------------------------
        FROM python:3.8-slim
        #FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

        #-----------------------------
        # 基本ライブラリのインストール
        #-----------------------------
        # インストール時のキー入力待ちをなくす環境変数
        ENV DEBIAN_FRONTEND noninteractive

        RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
            sudo \
            git \
            curl \
            wget \
            bzip2 \
            ca-certificates \
            libx11-6 \
            python3-pip \
            # imageのサイズを小さくするためにキャッシュ削除
            && apt-get clean \
            && rm -rf /var/lib/apt/lists/*

        RUN pip3 install --upgrade pip

        #-----------------------------
        # 環境変数
        #-----------------------------
        ENV LC_ALL=C.UTF-8
        ENV export LANG=C.UTF-8
        ENV PYTHONIOENCODING utf-8

        #-----------------------------
        # 追加ライブラリのインストール
        #-----------------------------
        RUN pip3 install fastapi
        RUN pip3 install uvicorn
        RUN pip3 install Gunicorn
        RUN pip3 install requests

        #-----------------------------
        # ソースコードの書き込み
        #-----------------------------
        COPY api/*.py /api/

        #-----------------------------
        # ポート開放
        #-----------------------------
        EXPOSE 5000

        #-----------------------------
        # コンテナ起動後に自動的に実行するコマンド
        #-----------------------------

        #-----------------------------
        # コンテナ起動後の作業ディレクトリ
        #-----------------------------
        WORKDIR /api
        ```

        > GKE 上で API を実行するので、docker image に API のソースコードを書き込む必要があることに注意

    1. API のデプロイメント定義ファイルを作成する<br>
        ```yml
        # FastAPI Pod
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: fast-api-pod
        spec:
        replicas: 3
        selector:
          matchLabels:
          app: fast-api-pod
        template:
          metadata:
            labels:                   
              app: fast-api-pod       
              version: svc                      #
            annotations:                                        # Istio を使用するためのアノテーション（key: value 形式の metadata）
              sidecar.istio.io/inject: "true"                   # Istio の Envoy（プロキシサーバー）サイドカーの挿入を行うかフラグ
              sidecar.istio.io/proxyCPU: "128m"                 # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU 量
              sidecar.istio.io/proxyMemory: "128Mi"             # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU メモリ
              proxy.istio.io/config: "{'concurrency':'4'}"      # Istio の Envoy（プロキシサーバー）サイドカーの並列スレッド数
        spec:
          containers:
            - name: fast-api-container
              image: gcr.io/my-project2-303004/fast-api-image-gke:latest
              imagePullPolicy: Always
              ports:
                - containerPort: 5000
              name: http-server
              command: ["/bin/sh","-c"]
              args: ["gunicorn app:app --bind 0.0.0.0:5000 -w 4 -k uvicorn.workers.UvicornWorker --reload"]
              resources:
              limits:
                cpu: 500m
                memory: "300Mi"
        ```

        ポイントは、以下の通り

        > `template.metadata.annotations` タグに、Istio を使用するためのアノテーション（key: value 形式の metadata）を追加している

        > 負荷耐性を正解に計測するために、`resources:limits` タグで、各 Pod の CPU リソース量を固定にしている

    1. API のサービス定義ファイルを作成する<br>
        ```yaml
        apiVersion: v1
        kind: Service
        metadata:
        name: fast-api-server
        spec:
        type: LoadBalancer
        ports:
            - port: 5000
            targetPort: 5000
            protocol: TCP
        selector:
            app: fast-api-pod  # デプロイメント定義ファイルで定義した Pod の識別名。app:sample-pod のラベルがつけられた Pod を通信先とする
        ```

1. vegeta atteck の構成<br>
    1. GKE にデプロイする docker image ための Dockerfile を作成する<br>
        ```dockerfile
        FROM golang:1.15.5-buster

        WORKDIR /vegeta/
        RUN apt-get -y update && \
            apt-get -y install apt-utils gcc curl && \
            apt-get clean && \
            go get -u github.com/tsenart/vegeta
        ```

    1. vegeta atteck のデプロイメント定義ファイルを作成する<br>
        ```yaml
        apiVersion: apps/v1         
        kind: Deployment            
        metadata:
        name: vegeta-attack-pod        
        spec:
        replicas: 1                    
        selector:
          matchLabels:
          app: vegeta-attack-pod     
        template:                      
          metadata:
            labels:                 
              app: vegeta-attack-pod
            annotations:                                      # Istio を使用するためのアノテーション（key: value 形式の metadata）
              sidecar.istio.io/inject: "true"                 # Istio の Envoy（プロキシサーバー）サイドカーの挿入を行うかフラグ
              sidecar.istio.io/proxyCPU: "128m"               # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU 量
              sidecar.istio.io/proxyMemory: "128Mi"           # Istio の Envoy（プロキシサーバー）サイドカーの使用 CPU メモリ
              proxy.istio.io/config: "{'concurrency':'16'}"   # Istio の Envoy（プロキシサーバー）サイドカーの並列スレッド数
          spec:
            containers:               
            - name: vegeta-attack-container                                     
              image: gcr.io/my-project2-303004/vegeta-attack-image-gke:latest   
              imagePullPolicy: Always
              command: ["tail","-f","/dev/null"]          # 
              resources:
                requests:
                  cpu: 1000m
                  memory: "1000Mi"
              volumeMounts:
                - name: vegeta-attack-configmap-volumes
                  mountPath: "/vegeta/configmap"
                  readOnly: true
            volumes:                      # ConfigMap 用のボリューム | ConfigMap は、ファイルとしてマウントすることで Pod から使用できる
              - name: vegeta-attack-configmap-volumes
              configMap:
                name: vegeta-attack-configmap
        ---
        apiVersion: v1
        kind: ConfigMap
        metadata:
            name: vegeta-attack-configmap
        data:
            # kye: value 形式で設定情報を定義する 
            get-health-target: "GET http://fast-api-server:5000/health"
            get-metadata-target: "GET http://fast-api-server:5000/metadata"
            post-add_users-target: "POST http://fast-api-server:5000/add_users Content-Type: application/json {'id':4, 'name':'user4', 'age':'100'}"
        ```

        > `template.metadata.annotations` タグに、Istio を使用するためのアノテーション（key: value 形式の metadata）を追加している

        > vegeta-attack CLI コマンド `vegeta attack` 後に続くコマンドは、テキストファイル (or echo "xxx") で指定する必要があるが、k8s で行う場合は ConfigMap で定義するのが最適になる

        > ConfigMap を Pod から使用するためには、環境変数に設定する方法と、ファイルとしてマウントする(Volume)方法の2つの方式がある。ここでは、後者の　ConfigMap をファイルとしてマウントする方法で、Pod から使用している

        mount した config map は、vegeta attack Pod のコンテナ内で以下のように構成される
        ```sh
        + /vegeta/ + configmap/ + get-health-target
        |          |            + get-metadata-target
        |          |            + post-add_users-target
        ```

1. Istio 用の k8s 定義ファイルを作成する
    1. DestinationRule 定義ファイルを作成する
        ```yml
        apiVersion: networking.istio.io/v1alpha3
        kind: DestinationRule
        metadata:
        name: fast-api-server
        spec:
        host: fast-api-server
        trafficPolicy:
          loadBalancer:
          simple: ROUND_ROBIN
          connectionPool:
          tcp:
            maxConnections: 100
          http:
            http1MaxPendingRequests: 100
            maxRequestsPerConnection: 100
          outlierDetection:
          consecutiveErrors: 100
          interval: 1s
          baseEjectionTime: 10m
          maxEjectionPercent: 10
        subsets:
          - name: svc
            labels:
              version: svc
        ```

        > - DestinationRule<br>
        >    k8s 内の通信に対して、どのような制限を掛けてあげるかを設定するための定義ファイル。Istio でのサーキットブレーカーの機能もこの DestinationRule で定義できる。

        >　サーキットブレーカーのしきい値は、サーキットブレーカーなしの Web-API が耐えられない負荷の 80% 程度になるしきい値が目安。

    1. VirtualService 定義ファイルを作成する
        ```yml
        apiVersion: networking.istio.io/v1alpha3
        kind: VirtualService
        metadata:
        name: fast-api-server
        spec:
        hosts:
          - fast-api-server
        http:
          - route:
            - destination:
              host: fast-api-server
              subset: svc
            weight: 100
        ```
        > - VirtualService
        >    k8s 内の通信に対して、この通信はこちらの Pod に流し、別の通信は別の Pod に流すといった設定をするための定義ファイル

1. ビルド構成ファイルを作成する
    CloudBuild を使用して、Fast API の docker image と vegeta attack の docker image を Google Container Registry に push するための ビルド構成ファイルを作成する
    ```yaml
    steps:
    #------------------------------------------------------
    # Fast API
    #------------------------------------------------------
    # キャッシュされたイメージを Container Registry から pull
    # 初めてイメージをビルドする際は docker pull で pull できる既存のイメージがないため、entrypoint を bash に設定し、コマンドの実行で返されるエラーを無視できるようにしている
    - name: 'gcr.io/cloud-builders/docker'
        entrypoint: 'bash'
        args: ['-c', 'docker pull gcr.io/${PROJECT_ID}/fast-api-image-gke:latest || exit 0']

    # Container Registry 上で docker image 作成 
    - name: 'gcr.io/cloud-builders/docker'
        id: docker build fast api
        args: [
        'build', 
        '-t', 'gcr.io/${PROJECT_ID}/fast-api-image-gke:latest', 
        '--cache-from', 'gcr.io/${PROJECT_ID}/fast-api-image-gke:latest',
        '-f', 'api/Dockerfile',
        '.'
        ]

    # Container Registry 上に docker image を登録
    - name: 'gcr.io/cloud-builders/docker'
        id: docker push fast api
        args: ['push', 'gcr.io/${PROJECT_ID}/fast-api-image-gke:latest']

    #------------------------------------------------------
    # vegeta attack
    #------------------------------------------------------
    - name: 'gcr.io/cloud-builders/docker'
        entrypoint: 'bash'
        args: ['-c', 'docker pull gcr.io/${PROJECT_ID}/vegeta-attack-image-gke:latest || exit 0']

    - name: 'gcr.io/cloud-builders/docker'
        id: docker build vegeta attack
        args: [
        'build', 
        '-t', 'gcr.io/${PROJECT_ID}/vegeta-attack-image-gke:latest', 
        '--cache-from', 'gcr.io/${PROJECT_ID}/vegeta-attack-image-gke:latest',
        '-f', 'vegeta/Dockerfile',
        '.'
        ]

    - name: 'gcr.io/cloud-builders/docker'
        id: docker push vegeta attack
        args: ['push', 'gcr.io/${PROJECT_ID}/vegeta-attack-image-gke:latest']

    #images: ['gcr.io/${PROJECT_ID}/fast-api-image-gke:latest']
    timeout: 3600s
    ```

1. ビルド構成ファイルを元に、docker image を Google Container Registry に push する<br>
    ```sh
    $ gcloud builds submit --config cloudbuild.yml
    ```

1. **Istio をインストールした GKE クラスタを作成する**<br>
    Istio を使用したサーキットブレーカーを導入するためには、通常の GKE クラスタを作成するのではなくて、Istio をインストールした GKE クラスタを作成する必要がある。
    Istio をインストールした GKE クラスタは、以下のコマンドで作成できる
    ```sh
    $ gcloud beta container clusters create ${CLUSTER_NAME} \
        --region ${ZONE} \
        --machine-type ${CPU_TYPE} \
        --min-nodes ${MIN_NODES} --max-nodes ${MAX_NODES} \
        --enable-autoscaling \
        --addons=Istio --istio-config=auth=MTLS_PERMISSIVE
    ```
    - `-addons=Istio` : Istio をインストールした GKE クラスタを作成する
    - `--istio-config` : セキュリティーオプション
        - `MTLS_STRICT` : 通信制限あり（mTLS 以外での通信を遮断）
        - `MTLS_PERMISSIVE` :通信制限なし（mTLS 以外での通信を遮断しない）

    > `--addons=Istio` `--istio-config` 引数を指定することで、GKE に Isto をインストールしている点がポイント

    > beta 版の `gcloud beta` を使用してクラスタ作成していることに注意

    > - mTLS : Mutual TLS authentication
    >     xxx

1. 作成した GKE クラスタに Istio が正常にインストールされているかを確認する<br>
    作成した GKE クラスタに Istio が正常にインストールされているかは、以下のコマンドで確認できる
    - Istio の Pod を確認<br>
        ```sh
        $ kubectl get pods -n istio-system
        ```

        インストール成功時の出力は、以下のようになる
        ```sh
        NAME                                             READY   STATUS      RESTARTS   AGE
        istio-citadel-f5586dffb-9dxml                    1/1     Running     0          3m24s
        istio-galley-7975f77bbf-fw8ht                    1/1     Running     0          3m23s
        istio-ingressgateway-b9477dcdb-7d2kz             1/1     Running     0          3m23s
        istio-pilot-59d4884d67-bl772                     2/2     Running     0          3m23s
        istio-policy-6885cb4644-7p7nn                    2/2     Running     1          3m23s
        istio-security-post-install-1.4.10-gke.8-8jb4s   0/1     Completed   0          2m51s
        istio-sidecar-injector-649d664b99-m7ppt          1/1     Running     0          3m23s
        istio-telemetry-59b6bf55c7-gktxl                 2/2     Running     0          3m23s
        istiod-istio-1611-6895859f65-k9p4d               1/1     Running     0          119s
        prometheus-6655946b9f-zd7f6                      2/2     Running     0          107s
        promsd-574ccb9745-fcknk                          2/2     Running     1          3m22s        
        ```

    - Istio の Service を確認<br>
        ```sh
        $ kubectl get service -n istio-system
        ```

        インストール成功時の出力は、以下のようになる
        ```sh
        NAME                     TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)                                                                                                                                      AGE
        istio-citadel            ClusterIP      10.51.253.160   <none>          8060/TCP,15014/TCP                                                                                                                           4m55s
        istio-galley             ClusterIP      10.51.255.116   <none>          443/TCP,15014/TCP,9901/TCP                                                                                                                   4m55s
        istio-ingressgateway     LoadBalancer   10.51.247.195   35.200.102.85   15020:30920/TCP,80:32634/TCP,443:31010/TCP,31400:30854/TCP,15029:30888/TCP,15030:31670/TCP,15031:30225/TCP,15032:30378/TCP,15443:30613/TCP   4m54s
        istio-pilot              ClusterIP      10.51.244.165   <none>          15010/TCP,15011/TCP,8080/TCP,15014/TCP                                                                                                       4m54s
        istio-policy             ClusterIP      10.51.245.123   <none>          9091/TCP,15004/TCP,15014/TCP                                                                                                                 4m54s
        istio-sidecar-injector   ClusterIP      10.51.240.223   <none>          443/TCP,15014/TCP                                                                                                                            4m54s
        istio-telemetry          ClusterIP      10.51.254.199   <none>          9091/TCP,15004/TCP,15014/TCP,42422/TCP                                                                                                       4m53s
        istiod-istio-1611        ClusterIP      10.51.252.210   <none>          15010/TCP,15012/TCP,443/TCP,15014/TCP,853/TCP                                                                                                3m28s
        prometheus               ClusterIP      10.51.254.10    <none>          9090/TCP                                                                                                                                     3m16s
        promsd                   ClusterIP      10.51.250.136   <none>          9090/TCP                                                                                                                                     4m53s
        ```

1. Istio の Envoy（プロキシサーバー）サイドカーを有効化する<br>
    デフォルトでは、Istio の Envoy サイドカーの各 Pod への挿入は、すべての k8s 名前空間で無効になっている。<br>
    そのため Envoy サイドカーを有効化する場合は、以下のコマンドで Envoy サイドカーの名前空間をアプリケーションのサービスに紐付ける必要がある
    ```sh
    $ kubectl label namespace ${NAME_SPACE} istio-injection=enabled    
    ```
    - `${NAME_SPACE}` : k8s 各種サービスの名前空間。<br>
        名前空間を使用していないときは、`default` を指定

    > 特定の Pod だけ Envoy サイドカーの挿入を行わないようにしたい場合は、k8s のデプロイメント定義ファイルの `template.metadata.annotations.sidecar.istio.io/inject` を `"false"` に設定すればよい

1. ConfigMap を作成する<br>
    vegeta attack 用のConfigMap を作成する
    ```sh
    $ kubectl apply -f k8s/configmap.yml
    ```

1. DestinationRule を作成する<br>
    Istio の DestinationRule を作成する
    ```sh
    $ kubectl apply -f k8s/destination_rule.yml
    ```

1. VirtualService を作成する<br>
    Istio の VirtualService を作成する
    ```sh
    $ kubectl apply -f k8s/virtual_service.yml
    ```

1. Pod を作成する<br>
    FastAPI と vegeta attack の Pod を作成する
    ```sh
    $ kubectl apply -f k8s/deployment.yml
    ```

1. Service を作成する<br>
    FastAPI を外部からアクセスするためのサービスを作成する
    ```sh
    $ kubectl apply -f k8s/service.yml
    ```

1. vegeta attack で負荷テストを行う（Pod内のコンテナから負荷テストを実施する場合）<br>
    vegeta attack の Pod 内のコンテナに接続し、コンテナ内から vegeta attack の CLI を用いて、負荷テストを行う<br>
    ```sh
    $ POD_NAME=vegeta-attack-pod-9979d6f67-szvgc
    $ DURATION=60s        # 負荷時間
    $ RATE=60             # 1sec あたりのリクエスト回数

    # vegeta attack を使用して負荷テスト
    # get-target, post-target は、config map で定義した設定値になる
    $ kubectl exec -i ${POD_NAME} -- bash -c "vegeta --version && \
        vegeta attack -duration=${DURATION} -rate=${RATE} -targets=/vegeta/configmap/get-health-target | vegeta report -type=text && \
        vegeta attack -duration=${DURATION} -rate=${RATE} -targets=/vegeta/configmap/get-metadata-target | vegeta report -type=text && \
        vegeta attack -duration=${DURATION} -rate=${RATE} -targets=/vegeta/configmap/post-add_users-target | vegeta report -type=text"
    ```

    > vegeta atteck は、ローカル PC から実行することもできる。わざわざ Pod として構成して、Pod 内のコンテナに入って実行するのは、負荷処理実施側のリソース使用量を固定にして、正確な負荷耐性を計測するため

1. vegeta attack で負荷テストを行う（ローカル環境から負荷テストを実施する場合）<br>
    ローカル環境から vegeta attack で負荷テストを行う場合は、以下の処理を実施する
    1. vegeta attack をローカル環境にインストールする
        ```sh
        # Mac OS の場合
        $ brew install vegeta
        ```
    1. vegeta attack の CLI を用いて、負荷テストを行う
        ```sh
        $ SERVICE_NAME=fast-api-server
        $ PORT=5000
        $ EXTERNAL_IP=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`
        $ DURATION=60s        # 負荷時間
        $ RATE=60             # 1sec あたりのリクエスト回数
        $ echo "GET http://${EXTERNAL_IP}:${PORT}/health" | vegeta attack -duration=${DURATION} -rate=${RATE} | vegeta report -type=text
        $ echo "GET http://${EXTERNAL_IP}:${PORT}/metadata" | vegeta attack -duration=${DURATION} -rate=${RATE} | vegeta report -type=text
        $ echo "POST http://${EXTERNAL_IP}:${PORT}/add_users Content-Type: application/json {'id':4, 'name':'user4', 'age':'100'}" | vegeta attack -duration=${DURATION} -rate=${RATE} | vegeta report -type=text
        ```

<!--
## ■ 負荷テストの結果


- サーキットブレーカーなし : health チェックのリクエスト
    ```sh
    ```
    ```sh
    ```

- サーキットブレーカーあり : health チェックのリクエスト
    ```sh
    Date: 
    Requests      [total, rate, throughput]         60000, 1000.02, 999.43
    Duration      [total, attack, wait]             1m0s, 59.999s, 31.224ms
    Latencies     [min, mean, 50, 90, 95, 99, max]  1.429ms, 38.142ms, 26.815ms, 89.062ms, 109.714ms, 168.068ms, 375.485ms
    Bytes In      [total, mean]                     900320, 15.01
    Bytes Out     [total, mean]                     0, 0.00
    Success       [ratio]                           99.99%
    Status Codes  [code:count]                      200:59996  503:4  
    Error Set:
    503 Service Unavailable
    ```
    ```sh
    Requests      [total, rate, throughput]         119997, 1999.75, 1247.62
    Duration      [total, attack, wait]             1m0s, 1m0s, 199.225ms
    Latencies     [min, mean, 50, 90, 95, 99, max]  238.67µs, 119.539ms, 75.13ms, 309.985ms, 403.164ms, 568.997ms, 956.997ms
    Bytes In      [total, mean]                     4762299, 39.69
    Bytes Out     [total, mean]                     0, 0.00
    Success       [ratio]                           62.60%
    Status Codes  [code:count]                      200:75113  503:44884  
    Error Set:
    503 Service Unavailable
    ```
    
    503 エラーは、サーキットブレーカーによる通信遮断。<br>
    サーキットブレーカーを導入することで、高負荷時の正常応答率が向上している。
-->

## 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter6_operation_management/load_test_pattern
- https://cloud.google.com/istio/docs/istio-on-gke/installing?hl=ja
- https://qiita.com/Ladicle/items/979d59ef0303425752c8
- https://qiita.com/Takagi_/items/129acd03e76fce5c295b
- https://qiita.com/cvusk/items/f1ab4644c8d1c161c056