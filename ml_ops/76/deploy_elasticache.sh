#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"
ZONE="us-west-2a"

IAM_ROLE_NAME="elasticache-iam-role"
IAM_POLICY_FILE_PATH="elasticache-iam-policy.json"

VPC_CIDR_BLOCK="10.0.0.0/16"
VPC_NAME="elasticache-vpc"

CACHE_SUBNET_CIDR_BLOCK="10.0.0.0/24"
CACHE_SUBNET_NAME="elasticache-cluster-subnet"
CACHE_SECURITY_GROUP_NAME="elasticache-cluster-security-group"
CACHE_SUBNET_GROUP_NAME="elasticache-subnet-group"
CACHE_PARAMETER_GROUP_NAME="elasticache-redis-parameter-group"
CACHE_CLUSTER_NAME="elasticache-redis-cluster"
CACHE_REPLICA_GROUP_NAME="elasticache-replica-group"
CACHE_REPLICA_CLUSTER_NAME="elasticache-replica-cluster"

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
# キャッシュクラスター作成
#=============================
mkdir -p log

#-----------------------------
# IAM を作成する
#-----------------------------
#if [ ! `aws iam list-roles --query 'Roles[*].RoleName' | grep ${IAM_ROLE_NAME}` ] ; then
#    # IAM ロールを作成する
#    aws iam create-role \
#        --role-name ${IAM_ROLE_NAME} \
#        --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH}"
#
#    # 作成した IAM ロールに IAM ポリシーを付与する
#    aws iam attach-role-policy \
#        --role-name ${IAM_ROLE_NAME} \
#        --policy-arn arn:aws:iam::aws:policy/AmazonElastiCacheFullAccess
#
#    sleep 5
#fi

#-----------------------------
# VPC を作成する
#-----------------------------
# VPC を作成
aws ec2 create-vpc --cidr-block ${VPC_CIDR_BLOCK} > log/${VPC_NAME}.json

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
	--cidr-block ${CACHE_SUBNET_CIDR_BLOCK} \
	--availability-zone ${ZONE} > log/${CACHE_SUBNET_NAME}.json

# サブネット ID を取得
CACHE_SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${CACHE_SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
echo "created cache subnet id=${CACHE_SUBNET_ID}"

# サブネットに名前をつける
aws ec2 create-tags --resources ${CACHE_SUBNET_ID} --tags Key=Name,Value=${CACHE_SUBNET_NAME}

#-----------------------------
# セキュリティーグループの作成
#-----------------------------
# セキュリティーグループの作成
#aws ec2 create-security-group \
#	--group-name ${CACHE_SECURITY_GROUP_NAME} \
#	--description "security group for connecting elasticache cluster from ec2 instance" \
#	--vpc-id ${VPC_ID}

# セキュリティグループIDを取得
SECURITY_GROUP_ID=$( aws ec2 describe-security-groups --filter "Name=vpc-id,Values=${VPC_ID}" --query SecurityGroups[0].GroupId --output text | grep sg- )
echo "created security-group id=${SECURITY_GROUP_ID}"

# セキュリティグループのインバウンドルールを設定（SSH接続）
aws ec2 authorize-security-group-ingress \
	--group-id ${SECURITY_GROUP_ID} \
    --protocol tcp \
	--port 22 \
	--cidr 0.0.0.0/0

# セキュリティグループのインバウンドルールを設定（キャッシュクラスターへの接続）
aws ec2 authorize-security-group-ingress \
	--group-id ${SECURITY_GROUP_ID} \
    --protocol tcp \
	--port 6379 \
	--cidr 0.0.0.0/0
	
aws ec2 create-tags --resources ${SECURITY_GROUP_ID} --tags Key=Name,Value=${CACHE_SECURITY_GROUP_NAME}

#-----------------------------
# サブネットグループを作成する
#-----------------------------
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name ${CACHE_SUBNET_GROUP_NAME} \
    --cache-subnet-group-description "subnet group" \
    --subnet-ids ${CACHE_SUBNET_ID} > log/${CACHE_SUBNET_GROUP_NAME}.json

#-----------------------------
# パラメータグループを作成する
#-----------------------------
aws elasticache create-cache-parameter-group \
	--cache-parameter-group-name ${CACHE_PARAMETER_GROUP_NAME}  \
	--cache-parameter-group-family  redis4.0 \
	--description "parameter group for redis4.0" > log/${CACHE_PARAMETER_GROUP_NAME}.json

#-----------------------------
# キャッシュクラスターを作成する
#-----------------------------
aws elasticache create-cache-cluster \
	--cache-cluster-id ${CACHE_CLUSTER_NAME} \
	--cache-parameter-group ${CACHE_SUBNET_GROUP_NAME} \
	--cache-parameter-group-name ${CACHE_PARAMETER_GROUP_NAME} \
	--engine redis \
	--engine-version 4.0.10 \
	--cache-node-type cache.t2.micro \
	--num-cache-nodes 1 > log/${CACHE_CLUSTER_NAME}.json

#	--security-group-ids ${SECURITY_GROUP_ID} \

#-----------------------------
# レプリケーショングループを作成する
#-----------------------------
aws elasticache create-replication-group \
	--replication-group-id ${CACHE_REPLICA_GROUP_NAME} \
	--primary-cluster-id ${CACHE_CLUSTER_NAME} \
	--replication-group-description 'my replication group'

#-----------------------------
# レプリカノードを追加する
#-----------------------------
aws elasticache create-cache-cluster \
	--cache-cluster-id ${CACHE_REPLICA_CLUSTER_NAME} \
	--replication-group-id ${CACHE_REPLICA_GROUP_NAME} \
	--preferred-availability-zone ${ZONE} > log/${CACHE_REPLICA_CLUSTER_NAME}.json
