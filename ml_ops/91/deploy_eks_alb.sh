#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
AWS_REGION=us-west-2

CLUSTER_NAME="eks-alb-cluster"
CLUSTER_NODE_TYPE="t2.medium"
MIN_NODES=1
MAX_NODES=2

IMAGE_NAME=predict-server-image-eks
ECR_REPOSITORY_NAME=${IMAGE_NAME}
#ENABLE_BUILD=0
ENABLE_BUILD=1

mkdir -p logs
#-----------------------------
# OS判定
#-----------------------------
if [ "$(uname)" = 'Darwin' ]; then
    OS='Mac'
    echo "Your platform is MacOS."  
elif [ "$(expr substr $(uname -s) 1 5)" = 'Linux' ]; then
    OS='Linux'
    echo "Your platform is Linux."  
elif [ "$(expr substr $(uname -s) 1 10)" = 'MINGW32_NT' ]; then                                                                                           
    OS='Cygwin'
    echo "Your platform is Cygwin."  
else
    echo "Your platform ($(uname -a)) is not supported."
    exit 1
fi

#-----------------------------
# AWS CLI のインストール
#-----------------------------
aws --version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
        sudo installer -pkg AWSCLIV2.pkg -target /
        rm AWSCLIV2.pkg
    elif [ ${OS} = "Linux" ] ; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm awscliv2.zip
    fi
fi
echo "aws version : `aws --version`"

#-----------------------------
# AWS デフォルト値の設定
#-----------------------------
# プロファイル作成 
if [ ! $( aws configure list-profiles | grep ${AWS_PROFILE} ) ] ; then
    aws configure --profile ${AWS_PROFILE}
fi

# AWS CLI を設定する環境変数
export AWS_ACCOUNTID=${AWS_ACCOUNT_ID}
export AWS_PROFILE=${AWS_PROFILE}
export AWS_DEFAULT_REGION=${AWS_REGION}

aws configure list
cat ~/.aws/config
cat ~/.aws/credentials

#-----------------------------
# eksctl コマンドをインストールする
#-----------------------------
eksctl version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        # Homebrew をインストール
        #/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

        # Weaveworks Homebrew tap をインストール
        brew tap weaveworks/tap

        # brew 経由で eksctl をインストール
        brew install weaveworks/tap/eksctl
    elif [ ${OS} = "Linux" ] ; then
        curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
        sudo mv /tmp/eksctl /usr/local/bin
    fi
fi

echo "eksctl version : `eksctl version`"

#-----------------------------
# kubectl コマンドをインストールする
#-----------------------------
kubectl version --client &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        # 最新版取得
        curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl

        # Ver指定(ex:1.40)
        curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.14.0/bin/darwin/amd64/kubectl

        # アクセス権限付与
        chmod +x ./kubectl
        sudo mv ./kubectl /usr/local/bin/kubectl
    elif [ ${OS} = "Linux" ] ; then
        curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"        
        chmod +x ./kubectl
        sudo mv ./kubectl /usr/local/bin/kubectl
    fi
fi

echo "kubectl version : `kubectl version`"

#-----------------------------
# jq コマンドのインストール
#-----------------------------
jq --version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
		brew install jq
    elif [ ${OS} = "Linux" ] ; then
		sudo apt -y update
		sudo apt -y install jq
    fi
fi
echo "jq version : `jq --version`"

#-----------------------------
# Amazon ECR に Docker image を push する
#-----------------------------
if [ ! ${ENABLE_BUILD} = 0 ] ; then
    # Docker image を作成する
    cd api/predict-server
    docker build ./ -t ${IMAGE_NAME}
    cd ../..

    # ECR リポジトリを作成する
    if [ "$( aws ecr batch-get-repository-scanning-configuration --repository-names ${ECR_REPOSITORY_NAME} --query scanningConfigurations[*].repositoryName | grep "${ECR_REPOSITORY_NAME}")" ] ; then
        if [ "$( aws ecr list-images --repository-name ${ECR_REPOSITORY_NAME} --query imageIds[*].imageTag | grep "latest")" ] ; then
            aws ecr batch-delete-image --repository-name ${ECR_REPOSITORY_NAME} --image-ids imageTag=latest
        fi
        aws ecr delete-repository --repository-name ${ECR_REPOSITORY_NAME}
    fi
    aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --image-scanning-configuration scanOnPush=true

    # ECR にログインする
    aws ecr get-login-password --profile ${AWS_PROFILE} --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

    # ローカルの docker image に ECR リポジトリ名での tag を付ける
    docker tag ${IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest

    # ECR に Docker image を push する
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest
fi

#-----------------------------
# クラスタを作成
#-----------------------------
if [ "$( aws eks list-clusters --query clusters | grep "${CLUSTER_NAME}")" ] ; then
    eksctl delete cluster --name ${CLUSTER_NAME} --region ${AWS_REGION} --wait
fi

if [ ! "$( aws eks list-clusters --query clusters | grep "${CLUSTER_NAME}")" ] ; then
    eksctl create cluster --name ${CLUSTER_NAME} \
        --node-type ${CLUSTER_NODE_TYPE} \
        --nodes-min ${MIN_NODES} --nodes-max ${MAX_NODES} \
        --managed
#        --fargate
fi

#-----------------------------------------------
# AWS Load Balancer Controller 用 IAM を作成する
#-----------------------------------------------
# AWS Load Balancer Controller 用の IAM policy を定義した json ファイルをダウンロードする
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.2/docs/install/iam_policy.json

# AWS Load Balancer Controller 用の IAM polciy を作成する
aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json

# load-balancer-role-trust-policy.json の Statement[0].Condition.StringEquals の部分を書き換え
OIDC=$( aws eks describe-cluster --name ${CLUSTER_NAME} --query "cluster.identity.oidc.issuer" --output text )
echo "OIDC : ${OIDC}"
#cat load-balancer-role-trust-policy.json | jq '.Statement[0].Condition.StringEquals[0]="${OIDC}"'

# AWS Load Balancer Controller 用の IAM role を作成する
aws iam create-role \
    --role-name AmazonEKSLoadBalancerControllerRole \
    --assume-role-policy-document file://"load-balancer-role-trust-policy.json" > logs/AmazonEKSLoadBalancerControllerRole.json

# IAM ロールに、必要な Amazon EKS 管理の IAM ポリシーをアタッチする
aws iam attach-role-policy \
    --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy \
    --role-name AmazonEKSLoadBalancerControllerRole

# k8s サービスアカウント用のマニフェストファイルをデプロイする
kubectl apply -f aws-load-balancer-controller-service-account.yaml

#-----------------------------
# AWS Load Balancer Controller をインストールする
#-----------------------------
# cert-manager をインストールする
kubectl apply \
    --validate=false \
    -f https://github.com/jetstack/cert-manager/releases/download/v1.5.4/cert-manager.yaml

# Load Balancer Controller のマニフェストをダウンロード
curl -Lo v2_4_2_full.yaml https://github.com/kubernetes-sigs/aws-load-balancer-controller/releases/download/v2.4.2/v2_4_2_full.yaml

# ダウンロードしたマニフェストを修正
sed -i.bak -e 's|your-cluster-name|${CLUSTER_NAME}|' ./v2_4_2_full.yaml

#-----------------------------
# API の各種 k8s リソースを作成する
#-----------------------------
kubectl apply -f k8s/predict.yml

kubectl get pods
kubectl get service
