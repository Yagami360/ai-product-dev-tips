# 【AWS】 `eksctl` コマンドを使用して Amazon EKS 上の Web API を構築する

Amazon EKS を用いて EKS クラスターを作成する方法には、以下の２種類がある

1. `eksctl` コマンドで EKS クラスターを作成する方法<br>
    `eksctl` コマンドで EKS クラスターを作成する場合は、EKS 用の VPC や IAM ロールの作成などが全て自動的に行われ、簡単に EKS クラスターを作成できる

1. `aws` コマンドで EKS クラスターを作成する方法<br>
    `aws` コマンドで EKS クラスターを作成する場合は、EKS 用の VPC や IAM ロールなどを自分で行う必要があるので、少し煩雑な方法になる

ここでは、最も容易な１つ目の `eksctl` コマンドで EKS クラスターを作成する方法を記載する。


## ■ 方法

1. AWS CLI をインストールする<br>
    - MacOS の場合<br>
        ```sh
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
        ```

    - Linux の場合<br>
        ```sh
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        ```

1. `eksctl` コマンドをインストールする
    EKS クラスターで多くの個別のタスクを自動化するために使用する AWS のコマンドラインツールである `eksctl` をインストールする

    - MacOS の場合<br>
        ```sh
        # Homebrew をインストール
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

        # Weaveworks Homebrew tap をインストール
        brew tap weaveworks/tap

        # brew 経由で eksctl をインストール
        brew install weaveworks/tap/eksctl
        ```

    - Linux の場合<br>
        ```sh
        curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
        sudo mv /tmp/eksctl /usr/local/bin
        ```

1. `kubectl` コマンドをインストールする
    - MacOS の場合<br>
        ```sh
        # 最新版取得
        $ curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl

        # アクセス権限付与
        $ chmod +x ./kubectl
        $ sudo mv ./kubectl /usr/local/bin/kubectl

        # インストール確認
        $ kubectl version
        ```

    - Linux の場合<br>
        ```sh
        $ curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
        $ chmod +x ./kubectl
        $ sudo mv ./kubectl /usr/local/bin/kubectl
        $ kubectl version
        ```

<!--
1. Amazon EKS クラスタにアクセスするための IAM を作成する<br>
    1. IAM ポリシーの内容を定義した json ファイルを作成<br>
        IAM ロールに割り当てるための IAM ポリシーの内容を定義した json ファイルを作成する
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "sts:AssumeRole"
                    ],
                    "Effect": "Allow",
                    "Principal": {
                        "Service": [
                            "eks.amazonaws.com"
                        ]
                    }
                }
            ]
        }
        ```

    1. IAM ロールを作成<br>
        `aws iam create-role` コマンドを使用して、EKS クラスターにアクセスするための IAM ロールを作成する
        ```sh
        aws iam create-role \
            --role-name ${IAM_ROLE_NAME} \
            --assume-role-policy-document "file://${IAM_ROLE_FILE_PATH}"
        ```
        - `--assume-role-policy-document` : IAM ポリシーの内容を定義した json ファイルを指定。

    1. 作成した IAM ロールにアクセス権限を付与する<br>
        作成した IAM ロールに、Lambda サービスにアクセスできるようにするための IAM ポリシーを付与する
        ```sh
        aws iam attach-role-policy \
            --role-name ${IAM_ROLE_NAME} \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        ```

    > AWS における IAM の仕組みの詳細は、「[【AWS】AWS の認証システム](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/58)」を参考
-->

1. API のコードを作成する<br>
    今回は FastAPI を使用した API のコードを作成する
    ```python
    import os
    import asyncio
    from datetime import datetime
    from time import sleep
    import logging

    from fastapi import FastAPI
    from pydantic import BaseModel
    from typing import Any, Dict

    from api_utils import graph_cut

    import sys
    sys.path.append(os.path.join(os.getcwd(), '../utils'))
    from utils import conv_base64_to_pillow, conv_pillow_to_base64

    # logger
    if not os.path.isdir("log"):
        os.mkdir("log")
    if( os.path.exists(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log')) ):
        os.remove(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
    logger = logging.getLogger(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
    logger.setLevel(10)
    logger_fh = logging.FileHandler(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
    logger.addHandler(logger_fh)

    # FastAPI
    app = FastAPI()
    print('[{}] time {} | 推論サーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    logger.info('[{}] time {} | 推論サーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

    class ImageData(BaseModel):
        """
        画像データのリクエストボディ
        """
        image: Any

    @app.get("/")
    async def root():
        return 'Hello API Server!\n'

    @app.get("/health")
    async def health():
        return {"health": "ok"}

    @app.get("/metadata")
    async def metadata():
        return

    @app.post("/predict")
    async def predict(
        img_data: ImageData,        # リクエストボディ    
    ):
        print('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
        logger.info('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

        # base64 -> Pillow への変換
        img_data.image = conv_base64_to_pillow(img_data.image)

        # OpenCV を用いて背景除去
        _, img_none_bg_pillow = graph_cut(img_data.image)

        # Pillow -> base64 への変換
        img_none_bg_base64 = conv_pillow_to_base64(img_none_bg_pillow)

        # 非同期処理の効果を明確化するためにあえて sleep 処理
        sleep(1)

        # レスポンスデータ設定
        print('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
        logger.info('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

        return {
            "status": "ok",
            "img_none_bg_base64" : img_none_bg_base64,
        }
    ```

1. API の Dockerfile を作成する<br>
    ```Dockerfile
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
    # miniconda のインストール
    RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
    RUN rm Miniconda3-latest-Linux-x86_64.sh
    ENV PATH=/miniconda/bin:${PATH}
    RUN conda update -y conda
        
    # conda 上で Python 3.6 環境を構築
    ENV CONDA_DEFAULT_ENV=py36
    RUN conda create -y --name ${CONDA_DEFAULT_ENV} python=3.6.9 && conda clean -ya
    ENV CONDA_PREFIX=/miniconda/envs/${CONDA_DEFAULT_ENV}
    ENV PATH=${CONDA_PREFIX}/bin:${PATH}
    RUN conda install conda-build=3.18.9=py36_3 && conda clean -ya

    # OpenCV3 のインストール
    RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends \
        libgtk2.0-0 \
        libcanberra-gtk-module \
        && sudo rm -rf /var/lib/apt/lists/*

    RUN conda install -y -c menpo opencv3=3.1.0 && conda clean -ya

    # Others
    RUN conda install -y tqdm && conda clean -ya
    RUN conda install -y -c anaconda pillow==6.2.1 && conda clean -ya
    RUN conda install -y -c anaconda requests && conda clean -ya
    RUN conda install -y -c conda-forge fastapi && conda clean -ya
    RUN conda install -y -c conda-forge uvicorn && conda clean -ya
    RUN conda install -y -c conda-forge Gunicorn && conda clean -ya
    RUN conda install -y -c conda-forge dataclasses && conda clean -ya
    RUN pip3 install contextlib2

    #-----------------------------
    # ソースコードの書き込み
    #-----------------------------
    WORKDIR /api/predict-server
    WORKDIR /api/utils
    COPY api/predict-server/ /api/predict-server/
    COPY api/utils/ /api/utils/

    #-----------------------------
    # ポート開放
    #-----------------------------

    #-----------------------------
    # コンテナ起動後に自動的に実行するコマンド
    #-----------------------------

    #-----------------------------
    # コンテナ起動後の作業ディレクトリ
    #-----------------------------
    WORKDIR /api/predict-server
    ```

<!--
1. API 用の固定 IP アドレスを確保する<br>
    ECR クラスター上の API Pod に Service 経由で外部アクセスするための固定 IP アドレスを確保する

    - GUI で行う場合<br>
        「[AWS の VPC コンソール画面](https://us-west-2.console.aws.amazon.com/vpc/home?region=us-west-2#Addresses:)」の Elastic IP 画面から「Elastic IP アドレスを割り当てる」ボタンをクリックする

    - CLI で行う場合<br>
        ```sh
        aws ec2 allocate-address --domain vpc --tag-specifications "ResourceType=elastic-ip,Tags=[{Key=Name,Value='${CLUSTER_NAME}-predict-server-ip'}]"
        ```
-->

1. Amazon ECR [Elastic Container Registry] に Docker image を push する<br>
    1. API の Docker image を作成する<br>
        ```sh
        cd api/predict-server
        docker build./  -t ${IMAGE_NAME}
        cd ../..
        ```
    1. ECR リポジトリを作成する<br>
        ```sh
        aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --image-scanning-configuration scanOnPush=true
        ```
    1. ECR にログインする<br>
        ```sh
        aws ecr get-login-password --profile ${AWS_PROFILE} --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
        ```
        > ECR を使用する場合は、`docker login` コマンドの `--username` オプションのユーザー名は `AWS` になる

        > `--profile` の値は `cat ~/.aws/config` で確認できる

    1. ローカルの docker image に ECR リポジトリ名での tag を付ける<br>
        ECR での docker image 名は ``${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest` になるので、`docker tag` でローカルにある docker image に別名をつける
        ```sh
        docker tag ${IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest
        ```
    1. ECR に Docker image を push する<br>
        ```sh
        docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest
        ```

1. API の k8s マニフェストを作成する<br>
    ```yaml
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
                image: 735015535886.dkr.ecr.us-west-2.amazonaws.com/predict-server-image-eks:latest
                command: ["/bin/sh","-c"]
                args: ["gunicorn app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5001 --workers 1 --threads 1 --backlog 256 --reload"]
    ---
    # Service
    apiVersion: v1
    kind: Service
    metadata:
    name: predict-server
    spec:
        #type: NodePort
        type: LoadBalancer
        loadBalancerIP: 44.225.109.227   # IP アドレス固定
    ports:
        - port: 5001
          targetPort: 5001
          protocol: TCP
    selector:
        app: predict-pod
    ```


    > EKS において `type: LoadBalancer` で Service リソースをデプロイした場合、`aacde1380ec0149da89649c5eebf63ab-1308085615.us-west-2.elb.amazonaws.com` のような URL で `EXTERNAL-IP` が割り当てられる。

    > [ToDo] 但し、この `EXTERNAL-IP` の URL に外部アクセスできなかった。原因は不明。URL で外部アクセスできるようにする

    > [ToDo] そのため、Elastic IP で作成した固定 IP を割り当てが、今度は `EXTERNAL-IP` が pending のままになってしまう。Elastic IP で外部アクセスできるようにする

1. EKS クラスターを作成する<br>
    ```sh
    eksctl create cluster --name ${CLUSTER_NAME} \
        --fargate \
        --node-type ${CLUSTER_NODE_TYPE} \
        --nodes-min ${MIN_NODES} --nodes-max ${MAX_NODES}
    ```
    - `--fargate` : 指定した場合は AWS Fargate で Linux アプリケーションを実行。指定しない場合はマネージド型ノードになる<br>

        > Fargate : Amazon EC2 インスタンスを管理せずに Kubernetes ポッドをデプロイできるサーバーレスコンピューティングエンジン

        > マネージド型ノード : Amazon EC2 インスタンスで Amazon Linux アプリケーションを実行する

    > Amazon EKS クラスターを使用するには、`[AmazonEKSClusterPolicy](https://us-east-1.console.aws.amazon.com/iam/home#/policies/arn:aws:iam::aws:policy/AmazonEKSClusterPolicy$jsonEditor)` という IAM ポリシーをもつ IAM ロールや VPC などが必要であるが、`eksctl` コマンドで EKS クラスターを作成すれば、この IAM ポリシー `AmazonEKSClusterPolicy` をもつ IAM ロールや VPC などが全て自動的に作成される。

    >`aws` コマンドで EKS クラスターを作成する場合は、EKS 用の VPC や IAM ロールを自分で作成する必要がある

1. 各種 k8s リソースをデプロイする<br>
    ```sh
    kubectl apply -f k8s/predict.yml
    ```

1. 【オプション】EKS クラスター・Pod・Service を確認する<br>
    EKS クラスター・Pod・Service を確認し、正常に動作していることを確認する

    - コンソール画面を使用する場合
        作成した EKS クラスターは、「[AWS の EKS コンソール画面](https://us-west-2.console.aws.amazon.com/eks/home?region=us-west-2#/clusters)」から確認できる。また、Pod や Service は、作成したクラスター内のコンソール画面から確認できる

        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170808767-a669d493-d180-4f4c-898d-261b62764d19.png"><br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170808821-c025e4ad-f296-433f-b7f4-3de90625a76f.png"><br>

    - CLI を使用する場合
        - Pod の確認
            ```sh
            kubectl get pod
            ```

        - Service の確認
            ```sh
            kubectl get service
            ```

1. 【オプション】APIのコンテナログ ＆ APIログを確認する<br>
    APIのコンテナログ ＆ APIログを確認するし、正常に動作していることを確認する

    - API のコンテナログ確認<br>
        ```sh
        kubectl logs `kubectl get pods | grep "predict-pod" | awk '{print $1}'`
        ```

    - API のコンテナログ確認<br>
        ```sh
        kubectl exec -it `kubectl get pods | grep "predict-pod" | awk '{print $1}'` /bin/bash
        cat log/app.log
        ```

<!--
1. セキュリティグループを設定する<br>
    GKE クラスター上にデプロイした `type: LoadBalancer` での Service の `EXTERNAL-IP` に外部アクセスできるようにするために、セキュリティグループを設定する

    - GUI で行う場合
        「[AWS の VPC コンソール画面](https://us-west-2.console.aws.amazon.com/vpc/home?region=us-west-2#securityGroups:)」から、セキュリティーグループを確認

    - CLI で行う場合
        ```sh
        ```
-->

1. EKS 上の API に対してリクエスト処理を行う<br>
    ```sh
    SERVICE_NAME=predict-server
    HOST=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`
    PORT=5001

    IN_IMAGES_DIR=in_images
    OUT_IMAGES_DIR=out_images
    rm -rf ${OUT_IMAGES_DIR}

    # リクエスト処理
    python3 request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR}
    ```

## ■ 参考サイト

- Amazon EKS
    - https://docs.aws.amazon.com/ja_jp/eks/latest/userguide/getting-started.html
    - https://docs.aws.amazon.com/ja_jp/eks/latest/userguide/getting-started-eksctl.html
    - https://dev.classmethod.jp/articles/aws-summit-online-2020-hol-06/
    - https://dev.classmethod.jp/articles/eks_basic/
- Amazon ECR
    - https://docs.aws.amazon.com/ja_jp/AmazonECR/latest/userguide/getting-started-cli.html

## ■ ToDO
- [ ] EKS において `type: LoadBalancer` で Service リソースをデプロイした場合、`aacde1380ec0149da89649c5eebf63ab-1308085615.us-west-2.elb.amazonaws.com` のような URL で `EXTERNAL-IP` が割り当てられるが、この URL に外部から `curl` でアクセスしても、API のエンドポイントにアクセスできなかったので、外部アクセスできるようにする
