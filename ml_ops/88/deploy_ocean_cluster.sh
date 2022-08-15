#!/usr/bin/env bash
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
AWS_REGION=us-west-2

CLUSTER_NAME=ocean-eks-cluster

# ${SPOTINST_ACCOUNT}, ${SPOTINST_TOKEN} を定義した外部ファイル読み込み（GitHub非公開）
. env.conf
echo "SPOTINST_ACCOUNT : ${SPOTINST_ACCOUNT}"
echo "SPOTINST_TOKEN : ${SPOTINST_TOKEN}"

#=============================
# OS判定
#=============================
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

#=============================
# AWS CLI のインストール
#=============================
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

#=============================
# AWS デフォルト値の設定
#=============================
# プロファイル作成 
if [ ! $( aws configure list-profiles | grep ${AWS_PROFILE} ) ] ; then
    aws configure --profile ${AWS_PROFILE}
fi
aws configure list

# AWS CLI を設定する環境変数
export AWS_ACCOUNTID=${AWS_ACCOUNT_ID}
export AWS_PROFILE=${AWS_PROFILE}
export AWS_DEFAULT_REGION=${AWS_REGION}

cat ~/.aws/config
cat ~/.aws/credentials

#=============================
# Spotinst の設定
#=============================
# Spotinst コンソール画面から Ocean クラスター作成

# Download the EKS cluster configuration 
aws eks update-kubeconfig --name ${CLUSTER_NAME}
cat ~/.kube/config

# Connect kubectl to your EKS cluster 
kubectl get svc

# spotinst-kubernetes-cluster-controller という名前の Pod をデプロイ
curl -fsSL http://spotinst-public.s3.amazonaws.com/integrations/kubernetes/cluster-controller/scripts/init.sh | \
    SPOTINST_TOKEN=${SPOTINST_TOKEN} \
    SPOTINST_ACCOUNT=${SPOTINST_ACCOUNT} \
    SPOTINST_CLUSTER_IDENTIFIER=${CLUSTER_NAME} \
    ENABLE_OCEAN_METRIC_EXPORTER=false \
    bash

# AWS 認証用 k8s の ConfigMap をダウンロード
curl -O https://amazon-eks.s3-us-west-2.amazonaws.com/1.10.3/2018-06-05/aws-auth-cm.yaml

# In the aws-auth-cm.yaml file, replace the <ARN of instance role (not instance profile)> snippet with the NodeInstanceRole value from the outputs tab of the EKS cluster CloudFormation Stack 
#cat ${} >> aws-auth-cm.yaml

# AWS 認証用 k8s の ConfigMap をデプロイ
kubectl apply -f aws-auth-cm.yaml 
