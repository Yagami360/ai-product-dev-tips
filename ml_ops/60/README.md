# 【AWS】Amazon EKS を用いて Web API を構築する

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

    > IAM の詳細は、「[【AWS】AWS の認証システム](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/58)」を参考
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
    ```

1. API の k8s マニフェストを作成する<br>
    ```yaml
    ```

1. EKS クラスターを作成する<br>
    ```sh
    eksctl create cluster --name ${CLUSTER_NAME} \
        --region ${REGION} \
        --fargate \
        --node-type ${CLUSTER_NODE_TYPE} \
        --nodes-min ${MIN_NODES} --nodes-max ${MAX_NODES}
    ```

    > Amazon EKS クラスターを使用するには、`[AmazonEKSClusterPolicy](https://us-east-1.console.aws.amazon.com/iam/home#/policies/arn:aws:iam::aws:policy/AmazonEKSClusterPolicy$jsonEditor)` という IAM ポリシーをもつ IAM ロールが必要であるが、`eksctl create cluster` コマンドで EKS クラスターを作成すれば、この IAM ポリシー `AmazonEKSClusterPolicy` をもつ IAM ロールが自動的に作成される。

1. 各種 k8s リソースをデプロイする<br>
    ```sh
    ```

## ■ 参考サイト

- https://docs.aws.amazon.com/ja_jp/eks/latest/userguide/getting-started.html
- xxx