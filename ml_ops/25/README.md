# GKE で構成した Web API に vegeta atteck を使用して負荷テストする

GKE で構成した Web API（FastAPI + uvicorn + gunicorn + docker での構成）に対して、vegeta atteck を使用して負荷テストを行う。<br>

ここでの構成例では、vegeta atteck を Pod として構成して Pod のコンテナ内部から負荷テストを行っているが、ローカル PC から vegeta atteck で負荷テストを行う方法もある。Pod 内部から負荷テストを行っているのは、負荷処理実施側のリソース使用量を固定にして、正確な負荷耐性を計測するためである。

<img src="https://user-images.githubusercontent.com/25688193/121793742-3fc6da00-cc3d-11eb-956f-40f408215570.png" width="800"><br>

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
        apiVersion: apps/v1         # Deployment の API バージョン。kubectl api-resources | grep Deployment と kubectl api-versions  | grep apps で確認可能  
        kind: Deployment            # デプロイメント定義ファイルであることを明示
        metadata:
        name: fast-api-pod        # 識別名
        spec:
        replicas: 3               # Pod の数
        selector:
            matchLabels:
            app: fast-api-pod          # template:metadata:labels:app と同じ値にする必要がある
        template:                      # Pod のテンプレート。このテンプレートをもとに ReplicaSet がレプリカ数の Pod を作成する
            metadata:
            labels:                    # Pod をクラスタ内で識別のするためのラベル。service.yml で Pod を識別するラベルとして使用される
                app: fast-api-pod        # 識別名。selector:matchLabels:app と同じ値にする必要がある
            spec:
            containers:                # Pod 内で動作させるコンテナ群の設定
            - name: fast-api-container                                     # コンテナ名
                image: gcr.io/my-project2-303004/fast-api-image-gke:latest     # Container Registry にアップロードした docker image
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
        apiVersion: apps/v1         # Deployment の API バージョン。kubectl api-resources | grep Deployment と kubectl api-versions  | grep apps で確認可能  
        kind: Deployment            # デプロイメント定義ファイルであることを明示
        metadata:
        name: vegeta-attack-pod        # 識別名
        spec:
        replicas: 1                    # Pod の数
        selector:
            matchLabels:
            app: vegeta-attack-pod     # template:metadata:labels:app と同じ値にする必要がある
        template:                      # Pod のテンプレート。このテンプレートをもとに ReplicaSet がレプリカ数の Pod を作成する
            metadata:
            labels:                    # Pod をクラスタ内で識別のするためのラベル。service.yml で Pod を識別するラベルとして使用される
                app: vegeta-attack-pod   # 識別名。selector:matchLabels:app と同じ値にする必要がある
            spec:
            containers:                # Pod 内で動作させるコンテナ群の設定
            - name: vegeta-attack-container                                     # コンテナ名
                image: gcr.io/my-project2-303004/vegeta-attack-image-gke:latest   # Container Registry にアップロードした docker image
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

        > ここでは、k8s v1.2 以降に導入された ConfigMap を使用して、vegeta-attack CLI で使用する "GET xxx" などの値を、key: value 形式の設定情報として定義しているが、ConfigMap を使用しなくとも、vegeta-attack CLI 実行時にこれらの値を直接指定すれば、負荷テストは行える

        > ConfigMap を Pod から使用するためには、環境変数に設定する方法と、ファイルとしてマウントする(Volume)方法の2つの方式がある。ここでは、後者の　ConfigMap をファイルとしてマウントする方法で、Pod から使用している

        mount した config map は、vegeta attack Pod のコンテナ内で以下のように構成される
        ```sh
        + /vegeta/ + configmap/ + get-health-target
        |          |            + get-metadata-target
        |          |            + post-add_users-target
        ```

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

1. GKE クラスタを作成する<br>
    ```sh
    $ gcloud container clusters create ${CLUSTER_NAME} \
        --region ${ZONE} \
        --machine-type ${CPU_TYPE} \
        --min-nodes ${MIN_NODES} --max-nodes ${MAX_NODES} \
        --enable-autoscaling
    ```

1. Pod を作成する<br>
    FastAPI と vegeta attack の Pod を作成する
    ```sh
    # API の Pod を作成する
    $ kubectl apply -f api/k8s/deployment.yml

    # vegeta attack の Pod を作成する
    $ kubectl apply -f vegeta/k8s/deployment.yml
    ```

1. Service を作成する<br>
    FastAPI を外部からアクセスするためのサービスを作成する
    ```sh
    $ kubectl apply -f api/k8s/service.yml
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

## 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter6_operation_management/load_test_pattern
- https://qiita.com/chidakiyo/items/f8cdfac7683216a29c56