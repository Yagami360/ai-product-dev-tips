#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
AWS_REGION=us-west-2

IMAGE_NAME=predict-server-image-eks
ECR_REPOSITORY_NAME=${IMAGE_NAME}

CLUSTER_NAME="eks-alb-cluster"

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
#aws configure list

# AWS CLI を設定する環境変数
export AWS_ACCOUNTID=${AWS_ACCOUNT_ID}
export AWS_PROFILE=${AWS_PROFILE}
export AWS_DEFAULT_REGION=${AWS_REGION}

#cat ~/.aws/config
#cat ~/.aws/credentials

#-----------------------------
# AWS リソース削除
#-----------------------------
# ECR リポジトリ
if [ "$( aws ecr batch-get-repository-scanning-configuration --repository-names ${ECR_REPOSITORY_NAME} --query scanningConfigurations[*].repositoryName | grep "${ECR_REPOSITORY_NAME}")" ] ; then
    if [ "$( aws ecr list-images --repository-name ${ECR_REPOSITORY_NAME} --query imageIds[*].imageTag | grep "latest")" ] ; then
        aws ecr batch-delete-image --repository-name ${ECR_REPOSITORY_NAME} --image-ids imageTag=latest
    fi
    aws ecr delete-repository --repository-name ${ECR_REPOSITORY_NAME}
fi

# EKS クラスター
if [ "$( aws eks list-clusters --query clusters | grep "${CLUSTER_NAME}")" ] ; then
    eksctl delete cluster --name ${CLUSTER_NAME} --region ${AWS_REGION} --wait
fi

# IAM role
if [ $( aws iam list-roles --query 'Roles[*].RoleName' | grep AmazonEKSLoadBalancerControllerRole ) ] ; then
    aws iam detach-role-policy --role-name AmazonEKSLoadBalancerControllerRole --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy
    aws iam delete-role --role-name AmazonEKSLoadBalancerControllerRole
fi

# IAM policy
if [ $( aws iam list-policies --query 'Policies[*].PolicyName' | grep AWSLoadBalancerControllerIAMPolicy ) ] ; then
    aws iam delete-policy --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy
fi
