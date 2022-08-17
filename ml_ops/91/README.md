# AWS Load Balancer Controller（旧 AWS ALB Ingress Controller）を使用して EKS 上の Web-API に ALB での L7 ロードバランシングを行う

k8s で構成した Web-API において、k8s マニフェストで `type:LoadBalancer` の Service リソースをデプロイすると、L4 / L7 ロードバランサーである CLB [Classic Load Balancer] / ELB を作成できるが、L7 の機能がより強化されている L7 ロードバランサーの ALB [Application Load Balancer] のほうを利用したいケースは多々ある。

ALB の作成自体は AWS コンソール画面た AWS CLI, terraform などから行うことができるが、ALB と URL の紐付けをコンソール画面や AWS CLI で行う場合は、その数が多いと面倒になってくる・

このような場合は、AWS Load Balancer Controller（旧 AWS ALB Ingress Controller）を使用すると便利である。

AWS Load Balancer Controller を使用することで、k8s の ingress を作成したタイミングで、ALB を作成することができる

> AWS Load Balancer Controller は、昔 AWS ALB Ingress Controller という名前だった

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

        > k8s の ServiceAccount リソース : k8s 内で管理されているアカウントで、Pod と紐づけることで Pod から各種 KubernetesAPIを操作できるようになる

1. k8s サービスアカウント用のマニフェストファイルをデプロイする<br>
    ```sh
    kubectl apply -f aws-load-balancer-controller-service-account.yaml
    ```

1. AWS Load Balancer Controller をインストールする
    1. cert-manager をインストールする
        ```sh
        kubectl apply \
            --validate=false \
            -f https://github.com/jetstack/cert-manager/releases/download/v1.5.4/cert-manager.yaml
        ```

    1. Load Balancer Controller をインストール
        ```sh
        # Load Balancer Controller のマニフェストをダウンロード
        curl -Lo v2_4_2_full.yaml https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases/download/v2.4.2/v2_4_2_full.yaml

        # ダウンロードしたマニフェストを修正する
        sed -i.bak -e 's|your-cluster-name|${CLUSTER_NAME}|' ./v2_4_2_full.yaml
        ```

    1. xxx

## ■ 参考サイト

- AWS Load Balancer Controller
    - https://docs.aws.amazon.com/ja_jp/eks/latest/userguide/aws-load-balancer-controller.html

- ALB Ingress Controller（古い方）
    - https://atmarkit.itmedia.co.jp/ait/articles/2003/24/news008.html
    - https://qiita.com/koudaiii/items/2031d67c715b5bb50357