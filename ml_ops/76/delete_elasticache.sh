#!/bin/sh
#set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"

IAM_ROLE_NAME="elasticache-iam-role"

VPC_CIDR_BLOCK="10.10.0.0/16"

CACHE_SUBNET_CIDR_BLOCK="10.10.0.0/24"
#CACHE_SUBNET_NAME="elasticache-cluster-subnet"
#CACHE_SECURITY_GROUP_NAME="elasticache-cluster-security-group"
CACHE_SUBNET_GROUP_NAME="elasticache-subnet-group"
CACHE_PARAMETER_GROUP_NAME="elasticache-redis-parameter-group"
CACHE_CLUSTER_NAME="elasticache-redis-cluster"

EC2_SUBNET_CIDR_BLOCK="10.10.0.0/32"
#EC2_SUBNET_NAME="elasticache-ec2-subnet"
#EC2_INTERNET_GATEWAY_NAME="elasticache-ec2-internet-gateway"
#EC2_ROUTE_TABLE_NAME="elasticache-ec2-route-table"
#EC2_SECURITY_GROUP_NAME="elasticache-ec2-security-group"

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
# EC2 インスタンスのリソース削除
#=============================
mkdir -p log
EC2_SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${EC2_SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep subnet- )
EC2_INTERNET_GATEWAY_ID=$( aws ec2 describe-internet-gateways --filter "Name=attachment.vpc-id,Values=${VPC_ID}" --query InternetGateways[*].InternetGatewayId --output text | grep igw- )
EC2_ROUTE_TABLE_ID=$( aws ec2 describe-route-tables --filter "Name=vpc-id,Values=${VPC_ID}" --query RouteTables[*].RouteTableId --putput text | grep rtb- )
EC2_INSTANCE_ID=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID}" --query Reservations[*].Instances[*].InstanceId --output text | grep i- )

# EC2 インスタンスの削除
if [ ${EC2_INSTANCE_ID} ] ; then
	aws ec2 terminate-instances --instance-ids "${EC2_INSTANCE_ID}"
	echo "deleted ec2-instances id=${EC2_INSTANCE_ID}"
fi

# サブネットを削除する
if [ ${EC2_SUBNET_ID} ] ; then
	aws ec2 delete-subnet --subnet-id ${EC2_SUBNET_ID}
	echo "deleted subnet id=${EC2_SUBNET_ID}"
fi

# 非メインのルートテーブルを削除（メインルートテーブルは VPC 削除時に削除される）
if [ ${EC2_ROUTE_TABLE_ID} ] ; then
	aws ec2 delete-route-table --route-table-id ${EC2_ROUTE_TABLE_ID}
	echo "route-table id=${EC2_ROUTE_TABLE_ID}"
fi

# インターネットゲートウェイを削除
if [ ${EC2_INTERNET_GATEWAY_ID} ] ; then
	aws ec2 detach-internet-gateway --internet-gateway-id ${EC2_INTERNET_GATEWAY_ID} --vpc-id ${VPC_ID}
	aws ec2 delete-internet-gateway --internet-gateway-id ${EC2_INTERNET_GATEWAY_ID}
	echo "deleted internet-gateway id=${EC2_INTERNET_GATEWAY_ID}"
fi

#=============================
# キャッシュクラスターのリソース削除
#=============================
# キャッシュクラスター
if [ $( aws elasticache describe-cache-clusters --query CacheClusters[*].CacheClusterId --output text | grep ${CACHE_CLUSTER_NAME} ) ] ; then
	aws elasticache delete-cache-cluster --cache-cluster-id ${CLUSTER_NAME} > log/${CACHE_CLUSTER_NAME}.json
	echo "deleted cache-cluster=${CACHE_CLUSTER_NAME}"
	sleep 180
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
SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${CACHE_SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
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
