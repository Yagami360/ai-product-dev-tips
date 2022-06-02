#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"

CLUSTER_NAME="eks-cluster"
CLUSTER_NODE_TYPE="t2.micro"
MIN_NODES=3
MAX_NODES=3

IMAGE_NAME=predict-server-image-eks
ECR_REPOSITORY_NAME=${IMAGE_NAME}
ENABLE_BUILD=0
#ENABLE_BUILD=1

APP_NAME="argoci-app"
REPOSITORY_URL="argoci-app"

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
# ArgoCD CLI のインストール
#-----------------------------
if [ ${OS} = "Mac" ] ; then
    brew install argocd
elif [ ${OS} = "Linux" ] ; then
    curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
    chmod +x /usr/local/bin/argocd
fi

echo "argocd version : `argocd version`"

#-----------------------------
# AWS デフォルト値の設定
#-----------------------------

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
    aws ecr get-login-password --profile ${AWS_PROFILE} --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

    # ローカルの docker image に ECR リポジトリ名での tag を付ける
    docker tag ${IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest

    # ECR に Docker image を push する
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest
fi

#-----------------------------
# API 用の固定 IP アドレスを確保する
#-----------------------------
#aws ec2 allocate-address --domain vpc --tag-specifications "ResourceType=elastic-ip,Tags=[{Key=Name,Value='${CLUSTER_NAME}-predict-server-ip'}]"

#-----------------------------
# クラスタを作成
#-----------------------------
if [ "$( aws eks list-clusters --query clusters | grep "${CLUSTER_NAME}")" ] ; then
    eksctl delete cluster --name ${CLUSTER_NAME} --region ${REGION} --wait
fi

if [ ! "$( aws eks list-clusters --query clusters | grep "${CLUSTER_NAME}")" ] ; then
    eksctl create cluster --name ${CLUSTER_NAME} \
        --node-type ${CLUSTER_NODE_TYPE} \
        --nodes-min ${MIN_NODES} --nodes-max ${MAX_NODES} \
        --managed
fi

#-----------------------------
# 各種 k8s リソースを作成する
#-----------------------------
# Web-API の k8s リソースをデプロイする
kubectl apply -f k8s/predict.yml

# ArgoCD の k8s リソースをデプロイする
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

#-----------------------------
# セキュリティーグループを設定
#-----------------------------

#-----------------------------
# ArgoCD API Server にアクセスする
#-----------------------------
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
ARGOCD_SERVER_DOMAIN=`kubectl describe service argocd-server --namespace argocd | grep "LoadBalancer Ingress" | awk '{print $3}'`
if [ ${OS} = "Mac" ] ; then
    open "https://${ARGOCD_SERVER_DOMAIN}" &
fi

#-----------------------------
# ArgoCD API Server にログインする
#-----------------------------
# パスワード確認
ARGOCD_USERNAME=`kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.username}" | base64 -d && echo`
ARGOCD_PASSWARD=`kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo`
echo `ArgoCD username : ${ARGOCD_USERNAME}`
echo `ArgoCD passward : ${ARGOCD_PASSWARD}`

# ログイン
argocd login ${ARGOCD_SERVER_DOMAIN} --name ${ARGOCD_USERNAME} --password ${ARGOCD_PASSWARD}

#-----------------------------
# ArgoCD で管理したい k8s マニフェストファイルと Git リポジトリーの同期を行う
#-----------------------------
# ArgoCD で管理するクラスターを選択し設定する
argocd cluster add ${CLUSTER_NAME}

# ArgoCD で管理する GitHub の k8s マニフェストファイルのフォルダーを設定
argocd app create ${APP_NAME} \
    --repo ${REPOSITORY_URL} \
    --path ${K8S_MANIFESTS_DIR} \
    --dest-server https://kubernetes.default.svc \
    --dest-namespace default
