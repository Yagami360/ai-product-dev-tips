#!/bin/sh
#set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"

IAM_ROLE_NAME="elasticache-iam-role"

VPC_CIDR_BLOCK="10.0.0.0/16"
CACHE_SUBNET_CIDR_BLOCK="10.0.0.0/24"
#CACHE_SUBNET_NAME="elasticache-cluster-subnet"
#CACHE_SECURITY_GROUP_NAME="elasticache-cluster-security-group"
CACHE_SUBNET_GROUP_NAME="elasticache-subnet-group"
CACHE_PARAMETER_GROUP_NAME="elasticache-redis-parameter-group"
CACHE_CLUSTER_NAME="elasticache-redis-cluster"
#CACHE_REPLICA_GROUP_NAME="elasticache-replica-group"
CACHE_REPLICA_GROUP_NAME="elasticache-cluster-replica-group"
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
#echo "aws version : `aws --version`"

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
#echo "jq version : `jq --version`"

#=============================
# AWS デフォルト値の設定
#=============================
# アカウントID
export AWS_ACCOUNTID=${AWS_ACCOUNT_ID}
#cat ~/.aws/credentials

# AWS CLI のプロファイル
export AWS_PROFILE=${AWS_PROFILE}
export AWS_DEFAULT_REGION=${REGION}
#cat ~/.aws/config

#=============================
# キャッシュクラスターのリソース削除
#=============================
mkdir -p log

# キャッシュクラスター
if [ $( aws elasticache describe-cache-clusters --query CacheClusters[0].CacheClusterId --output text | grep ${CACHE_CLUSTER_NAME} ) ] ; then
	aws elasticache delete-cache-cluster --cache-cluster-id ${CACHE_CLUSTER_NAME} > log/${CACHE_CLUSTER_NAME}.json
	echo "deleted cache-cluster=${CACHE_CLUSTER_NAME}"
	#sleep 180
fi

# レプリカノード（レプリカクラスター）
if [ $( aws elasticache describe-cache-clusters --query CacheClusters[1].CacheClusterId --output text | grep ${CACHE_REPLICA_CLUSTER_NAME} ) ] ; then
	aws elasticache delete-cache-cluster --cache-cluster-id ${CACHE_REPLICA_CLUSTER_NAME} > log/${CACHE_REPLICA_CLUSTER_NAME}.json
	echo "deleted replica-cluster=${CACHE_REPLICA_CLUSTER_NAME}"
	#sleep 180
fi

# レプリケーショングループ
if [ $( aws elasticache describe-replication-groups --query ReplicationGroups[0].ReplicationGroupId --output text | grep ${CACHE_REPLICA_GROUP_NAME} ) ] ; then
  aws elasticache delete-replication-group --replication-group-id ${CACHE_REPLICA_GROUP_NAME}
	echo "deleted replica-group=${CACHE_REPLICA_GROUP_NAME}"
fi

# サブネットグループ
if [ $( aws elasticache describe-cache-subnet-groups --query CacheSubnetGroups[*].CacheSubnetGroupName | grep ${CACHE_SUBNET_GROUP_NAME} ) ] ; then
	aws elasticache delete-cache-subnet-group --cache-subnet-group-name ${CACHE_SUBNET_GROUP_NAME}
	echo "deleted cache-subnet-group=${CACHE_SUBNET_GROUP_NAME}"
fi

# パラメータグループ
if [ $( aws elasticache describe-cache-parameter-groups --query CacheParameterGroups[*].CacheParameterGroupName | grep ${CACHE_PARAMETER_GROUP_NAME} ) ] ; then
	aws elasticache delete-cache-parameter-group --cache-parameter-group-name ${CACHE_PARAMETER_GROUP_NAME}
	echo "deleted cache-parameter-group=${CACHE_PARAMETER_GROUP_NAME}"
fi

# セキュリティーグループ
#VPC_ID=$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${VPC_CIDR_BLOCK}" --query Vpcs[*].VpcId --output text | grep "vpc-" )
#SECURITY_GROUP_ID=$( aws ec2 describe-security-groups --filter "Name=vpc-id,Values=${VPC_ID}" --query SecurityGroups[0].GroupId --output text | grep sg- )
#if [ ${SECURITY_GROUP_ID} ] ; then
#	aws ec2 delete-security-group --group-id ${SECURITY_GROUP_ID}
#	echo "deleted security-group id=${SECURITY_GROUP_ID}"
#fi

# サブネット
CACHE_SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${CACHE_SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
if [ ${CACHE_SUBNET_ID} ] ; then
	aws ec2 delete-subnet --subnet-id ${CACHE_SUBNET_ID}
	echo "deleted cahce subnet id=${CACHE_SUBNET_ID}"
fi

# VPC
VPC_ID=$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${VPC_CIDR_BLOCK}" --query Vpcs[*].VpcId --output text | grep "vpc-" )
if [ ${VPC_ID} ] ; then
	aws ec2 delete-vpc --vpc-id ${VPC_ID}
	echo "deleted vpc id=${VPC_ID}"
	sleep 10
fi

# IAM role
if [ $( aws iam list-roles --query 'Roles[*].RoleName' | grep ${IAM_ROLE_NAME} ) ] ; then
    aws iam detach-role-policy --role-name ${IAM_ROLE_NAME} --policy-arn arn:aws:iam::aws:policy/AmazonElastiCacheFullAccess
    aws iam delete-role --role-name ${IAM_ROLE_NAME}
fi
