#!/bin/sh
#set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"

IAM_ROLE_NAME="elasticache-iam-role"

VPC_CIDR_BLOCK="10.10.0.0/16"
SUBNET_CIDR_BLOCK="10.10.0.0/24"

SUBNET_GROUP_NAME="elasticache-subnet-group"
PARAMETER_GROUP_NAME="elasticache-redis-parameter-group"
CLUSTER_NAME="elasticache-redis-cluster"

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
# リソース削除
#=============================
mkdir -p log

# キャッシュクラスター
if [ $( aws elasticache describe-cache-clusters --query CacheClusters[*].CacheClusterId --output text | grep ${CLUSTER_NAME} ) ] ; then
	aws elasticache delete-cache-cluster --cache-cluster-id ${CLUSTER_NAME} > log/${CLUSTER_NAME}.json
	echo "deleted cache-cluster=${CLUSTER_NAME}"
	sleep 180
fi

# サブネットグループ
if [ $( aws elasticache describe-cache-subnet-groups --query CacheSubnetGroups[*].CacheSubnetGroupName | grep ${SUBNET_GROUP_NAME} ) ] ; then
	aws elasticache delete-cache-subnet-group --cache-subnet-group-name ${SUBNET_GROUP_NAME}
	echo "deleted cache-subnet-group=${SUBNET_GROUP_NAME}"
fi

# パラメータグループ
if [ $( aws elasticache describe-cache-parameter-groups --query CacheParameterGroups[*].CacheParameterGroupName | grep ${PARAMETER_GROUP_NAME} ) ] ; then
	aws elasticache delete-cache-parameter-group --cache-parameter-group-name ${PARAMETER_GROUP_NAME}
	echo "deleted cache-parameter-group=${PARAMETER_GROUP_NAME}"
fi

# サブネット
SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
if [ ${SUBNET_ID} ] ; then
	aws ec2 delete-subnet --subnet-id ${SUBNET_ID}
	echo "deleted subnet id=${SUBNET_ID}"
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
