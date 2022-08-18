# AWS Load Balancer Controller（旧 AWS ALB Ingress Controller）を使用して EKS 上の Web-API に ALB での L7 ロードバランシングを行う

k8s で構成した Web-API において、k8s マニフェストで `type:LoadBalancer` の Service リソースをデプロイすると、L4 / L7 ロードバランサーである CLB [Classic Load Balancer] / ELB を作成できるが、L7 の機能がより強化されている L7 ロードバランサーの ALB [Application Load Balancer] のほうを利用したいケースは多々ある。

ALB の作成自体は AWS コンソール画面た AWS CLI, terraform などから行うことができるが、ALB と URL の紐付けをコンソール画面や AWS CLI で行う場合は、その数が多いと面倒になってくる・

このような場合は、AWS Load Balancer Controller（旧 AWS ALB Ingress Controller）を使用すると便利である。

AWS Load Balancer Controller を使用することで、k8s の ingress を作成したタイミングで、ALB を作成することができる

> AWS Load Balancer Controller は、昔 AWS ALB Ingress Controller という名前だった

## ■ ToDo
- [ ] Web-API の Ingress リソースをデプロイ時に以下のエラーが発生しデプロイできないので、ALB も作成されない問題の解決
    ```sh
    Error from server (InternalError): error when creating "k8s/predict.yml": Internal error occurred: failed calling webhook "vingress.elbv2.k8s.aws": failed to call webhook: Post "https://aws-load-balancer-webhook-service.kube-system.svc:443/validate-networking-v1-ingress?timeout=10s": dial tcp 10.100.156.84:443: connect: connection refused
    ```

- [ ] ALB 作成後、EKS 上の Web-API へのリクエストがうまくロードバランシングされることを確認する方法を追加する

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

1. kubectl コマンドをインストールする
    - MacOS の場合
        ```sh
        # 最新版取得
        curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl

        # Ver指定(ex:1.40)
        curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.14.0/bin/darwin/amd64/kubectl

        # アクセス権限付与
        chmod +x ./kubectl
        sudo mv ./kubectl /usr/local/bin/kubectl
        ```

    - Ubuntu の場合<br>
        ```sh
        curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"        
        chmod +x ./kubectl
        sudo mv ./kubectl /usr/local/bin/kubectl
        ```

1. API のコードを作成する<br>
    今回は FastAPI を使用した API のコードを作成する。コア部分ではないので省略

1. API の Dockerfile を作成する<br>
    コア部分ではないので省略

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

1. AWS Load Balancer Controller 用の IAM policy を作成する<br>

    1. AWS Load Balancer Controller 用の IAM policy を定義した json ファイルをダウンロードする<br>
        ```sh
        curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.2/docs/install/iam_policy.json
        ```

    1. AWS Load Balancer Controller 用の IAM polciy を作成する<br>
        ```sh
        aws iam create-policy \
            --policy-name AWSLoadBalancerControllerIAMPolicy \
            --policy-document file://iam_policy.json
        ```

    1. IAM role を定義した json ファイルを作成する
        - `load-balancer-role-trust-policy.json`
            ```sh
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/oidc.eks.${AWS_REGION}.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE"
                        },
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {
                                "oidc.eks.${AWS_REGION}.amazonaws.com/id/${OIDC_ID}:aud": "sts.amazonaws.com",
                                "oidc.eks.${AWS_REGION}.amazonaws.com/id/${OIDC_ID}:sub": "system:serviceaccount:kube-system:aws-load-balancer-controller"
                            }
                        }
                    }
                ]
            }
            ```

            ここで、`${OIDC_ID}` の部分は、`aws eks describe-cluster --name ${CLUSTER_NAME} --query "cluster.identity.oidc.issuer" --output text` コマンド実行時にコンソール出力される `oidc.eks.${AWS_REGION}.amazonaws.com/id/$OIDC_ID{}` の `${OIDC_ID}` の値にすること

    1. AWS Load Balancer Controller 用の IAM role を作成する<br>
        ```sh
        aws iam create-role \
            --role-name AmazonEKSLoadBalancerControllerRole \
            --assume-role-policy-document file://"load-balancer-role-trust-policy.json"
        ```

    1. IAM ロールに、必要な Amazon EKS 管理の IAM ポリシーをアタッチする
        ```sh
        aws iam attach-role-policy \
            --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy \
            --role-name AmazonEKSLoadBalancerControllerRole
        ```

1. AWS Load Balancer Controller の k8s サービスアカウント用のマニフェストファイルを作成する
    - `aws-load-balancer-controller-service-account.yaml`
        ```yml
        apiVersion: v1
        kind: ServiceAccount
        metadata:
        labels:
            app.kubernetes.io/component: controller
            app.kubernetes.io/name: aws-load-balancer-controller
        name: aws-load-balancer-controller
        namespace: kube-system
        annotations:
            eks.amazonaws.com/role-arn: arn:aws:iam::${AWS_ACCOUNT_ID}:role/AmazonEKSLoadBalancerControllerRole
        ```

        > - k8s の ServiceAccount リソース<br>
        > k8s 内で管理されているアカウントで、Pod と紐づけることで Pod から各種 KubernetesAPI を操作できるようになる。<br>
        > 特に EKS の場合で話を限定すると、Pod に適切な IAM ポリシーを付与した IAM ロールを割り当てることで、Pod 内から各種 AWS サービスにアクセスできるようになる？

1. k8s サービスアカウント用のマニフェストファイルをデプロイする<br>
    ```sh
    kubectl apply -f aws-load-balancer-controller-service-account.yaml
    ```

1. AWS Load Balancer Controller をインストールする
    1. cert-manager をインストールする（cert-manager の k8s マニフェストをデプロイする）<br>
        cert-manager は、kubernetes クラスタ上で SSL/TLS 証明書（https通信のための認証）の取得・更新・利用を簡単に行えるツール（実体は Issuer, Certificate, Ingress などの k8s リソース郡）であるが、以下のコマンドで cert-manager を k8s クラスターにデプロイする。
        
        > 参考サイト : https://zenn.dev/masaaania/articles/e54119948bbaa2

        ```sh
        kubectl apply \
            --validate=false \
            -f https://github.com/jetstack/cert-manager/releases/download/v1.5.4/cert-manager.yaml
        ```

        上記コマンド実行後、以下のような cert-manager 関連の k8s リソースがデプロイされる

        - Pod
            ```sh
            NAMESPACE      NAME                                       READY   STATUS    RESTARTS           AGE
            cert-manager   cert-manager-594bcb5484-dxqlg              1/1     Running   0                  3m2s
            cert-manager   cert-manager-cainjector-544bcd9bfc-hp5vj   1/1     Running   0                  3m2s
            cert-manager   cert-manager-webhook-5999fd64fb-v9vld      1/1     Running   0                  3m2s            
            ```

        - Service
            ```sh
            NAMESPACE      NAME                   TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                  AGE
            cert-manager   cert-manager           ClusterIP   10.101.249.108   <none>        9402/TCP                 2m1s
            cert-manager   cert-manager-webhook   ClusterIP   10.102.12.224    <none>        443/TCP                  2m1s
            ```

        - ConfigMap
            ```sh
            NAMESPACE         NAME                                      DATA   AGE
            cert-manager      kube-root-ca.crt                          1      3m50s
            ```

        - Secret
            ```sh
            NAMESPACE      NAME                      TYPE     DATA   AGE
            cert-manager   cert-manager-webhook-ca   Opaque   3      3m39s            
            ```

    1. Load Balancer Controller のマニフェストをダウンロードする
        ```sh
        # Load Balancer Controller のマニフェストをダウンロード
        curl -Lo v2_4_2_full.yaml https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases/download/v2.4.2/v2_4_2_full.yaml
        ```

    1. ダウンロードしたマニフェストを修正する
        ```sh
        # ダウンロードしたマニフェストを修正する
        sed -i.bak -e 's|your-cluster-name|${CLUSTER_NAME}|' ./v2_4_2_full.yaml
        ```
        > `${CLUSTER_NAME}` の部分は、（`eks-alb-cluster` など）に変更すること

        更に、`v2_4_2_full.yaml` の 以下の ServiceAccount の部分を削除する
        ```sh
        apiVersion: v1
        kind: ServiceAccount
        metadata:
            labels:
                app.kubernetes.io/component: controller
                app.kubernetes.io/name: aws-load-balancer-controller
            name: aws-load-balancer-controller
            namespace: kube-system
        ---
        ```

        > 先にデプロイした `aws-load-balancer-controller-service-account.yaml` で、Load Balancer Controller 用のサービスアカウントをデプロイしているので、`v2_4_2_full.yaml` のサービスアカウントは削除する

    1. Load Balancer Controller をデプロイする
        ```sh
        kubectl apply -f v2_4_2_full.yaml
        ```

        上記コマンド実行後、以下のような k8s リソースが追加される。
        
        `aws-load-balancer-controller` という名前の Deployment (Pod) が、ALB を自動的に作成する pod であるが、この時点では Web-API のマニフェストの Ingress をデプロイしてないので、まだ ALB は作成されないことに注意

        - Deployment
            ```sh
            NAMESPACE      NAME                           READY   UP-TO-DATE   AVAILABLE   AGE
            kube-system    aws-load-balancer-controller   0/1     0            0           3m15s
            ```

        - Service
            ```sh
            NAMESPACE      NAME                                TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                  AGE
            kube-system    aws-load-balancer-webhook-service   ClusterIP   10.100.156.84    <none>        443/TCP                  49s
            ```

        - Secret
            ```sh
            NAMESPACE      NAME                            TYPE                DATA   AGE
            kube-system    aws-load-balancer-webhook-tls   kubernetes.io/tls   3      2m1s
            ```

1. WEb-API の k8s マニフェストを作成する
    ```sh
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
    #  annotations:
    #    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: tcp
    #    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    #    service.beta.kubernetes.io/aws-load-balancer-eip-allocations: eipalloc-022b9722973f6a222
    spec:
    type: NodePort
    #  type: LoadBalancer
    #  loadBalancerIP: 44.225.109.227   # IP アドレス固定
    ports:
        - port: 5001
        targetPort: 5001
        protocol: TCP
    selector:
        app: predict-pod
    ---
    # Ingress
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
    name: predict-ingress
    annotations:
        kubernetes.io/ingress.class: alb
        alb.ingress.kubernetes.io/scheme: internet-facing
        alb.ingress.kubernetes.io/tags: Environment=dev,Team=test
    spec:
    rules:
    - http:
        paths:
        - path: /
            pathType: Prefix
            backend:
            service:
                name: predict-server
                port:
                number: 5001
    ```

    ポイントは、以下の通り

    - Ingress を作成するので、NodePort の Service を作成する

    - Kubernetes v1.22 では `apiVersion: networking.k8s.io/v1beta1` での Ingress など様々なベータ API が削除されていることに注意

    - xxx

1. Web-API の k8s マニフェストをプロイする<br>
    ```sh
    kubectl apply -f k8s/predict.yml
    ```

    上記 k8s マニフェストに含まれる Ingress がデプロイされた時点で、`aws-load-balancer-controller` という名前の Deployment (Pod) が、ALB を自動的に作成する

1. ALB が作成されていることを確認する
    「[AWS ロードバランサーのコンソール画面](https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#LoadBalancers:sort=loadBalancerName)」 から、ALB が作成されていることを確認する


    > [ToDo] `aws-load-balancer-controller` という名前の Deployment (Pod) をデプロイしたが、ALB が作成されていないので、うまく作成されるようにする

1. EKS 上の Web-API にリクエストし、うまくロードバランシングされていることを確認する<br>
    xxx

## ■ 参考サイト

- AWS Load Balancer Controller
    - https://docs.aws.amazon.com/ja_jp/eks/latest/userguide/aws-load-balancer-controller.html
    - https://qiita.com/mksamba/items/c0e41a2a63e62a50aea3

- ALB Ingress Controller（古い方）
    - https://atmarkit.itmedia.co.jp/ait/articles/2003/24/news008.html
    - https://qiita.com/koudaiii/items/2031d67c715b5bb50357