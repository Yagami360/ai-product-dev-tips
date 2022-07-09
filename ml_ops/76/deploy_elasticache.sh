#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"
ZONE="us-west-2a"

IAM_ROLE_NAME="elasticache-iam--role"
IAM_POLICY_FILE_PATH="elasticache-iam-policy.json"

VPC_CIDR_BLOCK="10.10.0.0/16"
VPC_NAME="elasticache-vpc"
SUBNET_CIDR_BLOCK="10.10.0.0/24"
SUBNET_NAME="elasticache-subnet"

SUBNET_GROUP_NAME="elasticache-subnet-group"
CLUSTER_NAME="elasticache-redis-cluster"
PARAMETER_GROUP_NAME="elasticache-redis-parameter-group"

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
# jq コマンドのインストール
#=============================
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

#=============================
# AWS デフォルト値の設定
#=============================
# アカウントID
export AWS_ACCOUNTID=${AWS_ACCOUNT_ID}
cat ~/.aws/credentials

# AWS CLI のプロファイル
export AWS_PROFILE=${AWS_PROFILE}
export AWS_DEFAULT_REGION=${REGION}
cat ~/.aws/config

#=============================
# リソース削除
#=============================
sh delete_elasticache.sh

#=============================
# リソース作成
#=============================
#-----------------------------
# IAM を作成する
#-----------------------------
# AWSBatchServiceRole
if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME}` ] ; then
    # IAM ロールを作成する
    aws iam create-role \
        --role-name ${IAM_ROLE_NAME} \
        --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH}"

    # 作成した IAM ロールに IAM ポリシーを付与する
    aws iam attach-role-policy \
        --role-name ${IAM_ROLE_NAME} \
        --policy-arn arn:aws:iam::aws:policy/AmazonElastiCacheFullAccess

    sleep 5
fi

#-----------------------------
# VPC を作成する
#-----------------------------
# VPC を作成
aws ec2 create-vpc --cidr-block ${VPC_CIDR_BLOCK}

# 作成した VPC の VPC ID 取得
VPC_ID=$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${VPC_CIDR_BLOCK}" --query Vpcs[*].VpcId --output text | grep "vpc-" )
echo "created vpc id=${VPC_ID}"

# VPC に名前をつける
aws ec2 create-tags --resources ${VPC_ID} --tags Key=Name,Value=${VPC_NAME}

#-----------------------------
# サブネットを作成する
#-----------------------------
# サブネットマスクを作成
aws ec2 create-subnet \
	--vpc-id ${VPC_ID} \
	--cidr-block ${SUBNET_CIDR_BLOCK} \
	--availability-zone ${ZONE}

# サブネット ID を取得
SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
echo "created subnet id=${SUBNET_ID}"

# サブネットに名前をつける
aws ec2 create-tags --resources ${SUBNET_ID} --tags Key=Name,Value=${SUBNET_NAME}

#-----------------------------
# サブネットグループを作成する
#-----------------------------
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name ${SUBNET_GROUP_NAME} \
    --cache-subnet-group-description "subnet group" \
    --subnet-ids ${SUBNET_ID}

#-----------------------------
# パラメータグループを作成する
#-----------------------------
aws elasticache create-cache-parameter-group \
	--cache-parameter-group-name ${PARAMETER_GROUP_NAME}  \
	--cache-parameter-group-family  redis4.0 \
	--description "parameter group for redis4.0"

#-----------------------------
# キャッシュクラスターを作成する
#-----------------------------
aws elasticache create-cache-cluster \
	--cache-cluster-id ${CLUSTER_NAME} \
	--cache-parameter-group ${SUBNET_GROUP_NAME} \
	--cache-parameter-group-name ${PARAMETER_GROUP_NAME} \
	--engine redis \
	--engine-version 3.2.4 \
	--cache-node-type cache.t2.micro \
	--num-cache-nodes 1
