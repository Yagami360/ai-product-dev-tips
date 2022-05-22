#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
REGION="us-west-2"

IAM_ROLE_NAME="eks-iam-role"
IAM_POLICY_FILE_PATH="eks-iam-policy.json"

CLUSTER_NAME="eks-cluster"
CLUSTER_NODE_TYPE="t2.micro"
MIN_NODES=1
MAX_NODES=1

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
aws --version

#-----------------------------
# kubectl コマンドをインストールする
#-----------------------------
<<COMMENTOUT
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

kubectl version
COMMENTOUT

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
# AWS デフォルト値の設定
#-----------------------------

#-----------------------------
# EKS 用 IAM 作成
#-----------------------------
<<COMMENTOUT
if [ `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME}` ] ; then
    aws iam delete-role --role-name ${IAM_ROLE_NAME}
fi

if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME}` ] ; then
    # Lambda 関数実行のための IAM ロールを作成する
    aws iam create-role \
        --role-name ${IAM_ROLE_NAME} \
        --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH}" &

    sleep 10

    # 作成した IAM ロールに、Lambda サービスにアクセスできるようにするための IAM ポリシーを付与する
    #aws iam attach-role-policy \
    #    --role-name ${IAM_ROLE_NAME} \
    #    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
fi
COMMENTOUT

#-----------------------------
# クラスタを作成
#-----------------------------
if [ "$( aws eks list-clusters --query clusters | grep "${CLUSTER_NAME}")" ] ; then
    kubectl delete svc kube-dns -n kube-system
    kubectl delete svc kubernetes
    eksctl delete cluster --name ${CLUSTER_NAME} --region ${REGION} --wait
fi

if [ ! "$( aws eks list-clusters --query clusters | grep "${CLUSTER_NAME}")" ] ; then
    eksctl create cluster --name ${CLUSTER_NAME} \
        --region ${REGION} \
        --fargate \
        --node-type ${CLUSTER_NODE_TYPE} \
        --nodes-min ${MIN_NODES} --nodes-max ${MAX_NODES}
fi

#-----------------------------
# 各種 k8s リソースを作成する
#-----------------------------

