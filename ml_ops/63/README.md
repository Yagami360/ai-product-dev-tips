# ArgoCD を使用して Web-API を Kubernetes（Amazon EKS）上に継続的にデプロイ（CD）する

ArgoCD は、git を起点とした Kubernetes リソースに対しての CD（デプロイ）ツールである。

Github Actions のような CI/CD ツールを利用して Kubernetes へのデプロイまで一貫した CI/CD パイプラインを作ることも可能でであるが、ArgoCD を使用すれば Kubernetes への CD が容易に実現でき、更に Github Actions などの CI ツールと組み込せることで、Kubernetes への CI/CD をより容易に実現できるメリットがある

> - GitOps<br>
>    Git コマンド（git push, git pull など）を起点として Kubernetes のリソースの CI/CD を行う仕組み


ここでは、Web-API を Amazon EKS 上に継続的にデプロイする方法を記載する

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

1. ArgoCD CLI をインストールする<br>
    - MacOS の場合<br>    
        ```sh
        brew install argocd
        ```

    - Linux の場合<br>
        ```sh
        curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
        chmod +x /usr/local/bin/argocd
        ```

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
        --node-type ${CLUSTER_NODE_TYPE} \
        --nodes-min ${MIN_NODES} --nodes-max ${MAX_NODES} \
        --managed
    ```
    - `--fargate` : 指定した場合は AWS Fargate で Linux アプリケーションを実行。指定しない場合はマネージド型ノードになる<br>

        > Fargate : Amazon EC2 インスタンスを管理せずに Kubernetes ポッドをデプロイできるサーバーレスコンピューティングエンジン

        > マネージド型ノード : Amazon EC2 インスタンスで Amazon Linux アプリケーションを実行する

        > `--fargate` を指定すると、ArgoCD Pod が正常に起動しないので、`--fargate` 指定なしで EKS クラスターを作成する必要があることに注意

    > Amazon EKS クラスターを使用するには、`[AmazonEKSClusterPolicy](https://us-east-1.console.aws.amazon.com/iam/home#/policies/arn:aws:iam::aws:policy/AmazonEKSClusterPolicy$jsonEditor)` という IAM ポリシーをもつ IAM ロールや VPC などが必要であるが、`eksctl` コマンドで EKS クラスターを作成すれば、この IAM ポリシー `AmazonEKSClusterPolicy` をもつ IAM ロールや VPC などが全て自動的に作成される。

    >`aws` コマンドで EKS クラスターを作成する場合は、EKS 用の VPC や IAM ロールを自分で作成する必要がある

1. 各種 k8s リソースをデプロイする<br>
    ```sh
    kubectl apply -f k8s/predict.yml
    ```

1. ArgoCD の k8s リソースをデプロイする<br>
    ArgoCD は、k8s の Pod して動作するので、作成した EKS クラスターに ArgoCD の k8s リソースをデプロイする
    ```sh
    kubectl create namespace argocd
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
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
            kubectl get pod -n argocd
            ```

        - Service の確認
            ```sh
            kubectl get service
            kubectl get service -n argocd
            ```

1. ArgoCD API Server にブラウザアクセスする<br>
    ArgoCD の k8s リソースデプロイ時に作成される ArgoCD の Service (ArgoCD API Server) にアクセスすることで、ArgoCD のコンソール画面に移動することができる

    以下のコマンドでは、ArgoCD API Server の Service を `"type": "LoadBalancer"` に変更して、`EXTERNAL-IP` を発行し、その URL にブラウザアクセスするようにしている

    ```sh
    kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
    ARGOCD_SERVER_DOMAIN=`kubectl describe service argocd-server | grep "LoadBalancer Ingress" | awk '{print $3}'`
    open "https://${ARGOCD_SERVER_DOMAIN}"
    ```

1. ArgoCD にログインする<br>
    ```sh
    argocd login ${ARGOCD_SERVER_DOMAIN} --name ${ARGOCD_USERNAME} --password ${ARGOCD_PASSWARD}
    ```
    - `--name` : ログインユーザー名。デフォルトでは `admin`
    - `--password` : ログインパスワード。デフォルトでは、`kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo` で取得可能

    > 初期ログインのアカウントは、作成した ArgoCD k8s リソースの Secret リソースに記載されている

1. ArgoCD で管理したい k8s マニフェストファイルと Git リポジトリーの同期を行う<br>
    1. ArgoCD で管理するクラスターを選択し設定する<br>
        ```sh
        argocd cluster add ${CLUSTER_NAME}
        ```
    1. ArgoCD で管理する GitHub の k8s マニフェストファイルのフォルダーを設定<br>
        ```sh
        argocd app create ${APP_NAME} --repo ${REPOSITORY_URL} --path ${K8S_MANIFESTS_DIR} --dest-server https://kubernetes.default.svc --dest-namespace default
        ```

<!--
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
-->

## ■ 参考サイト

- https://qiita.com/bindingpry/items/8f10a701015599a00953
- https://dev.classmethod.jp/articles/getting-started-argocd/
- https://qiita.com/MahoTakara/items/b52c2bdd1243c8190ee9
- https://sotoiwa.hatenablog.com/entry/2020/05/25/184227
