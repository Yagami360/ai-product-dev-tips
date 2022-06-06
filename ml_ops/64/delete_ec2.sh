#!/bin/sh
set -eu
REGION="us-west-2"
ZONE="us-west-2a"

CIDR_BLOCK=10.10.0.0
VPC_NAME="datadog-ec2-vpc"
SUBNET_NAME="datadog-ec2-subnet"
INTERNET_GATEWAY_NAME="datadog-ec2-internet-gateway"
ROUTE_TABLE_NAME="datadog-ec2-route-table"
SECURITY_GROUP_NAME="datadog-ec2-security-group"

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
# EC2 リソースを削除する（各種リソースが関連付けられているので削除順に注意）
#-----------------------------
VPC_ID=`aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${CIDR_BLOCK}/16" --query Vpcs[*].VpcId | grep vpc- | sed 's/ //g' | sed 's/"//g'`
SUBNET_ID=`aws ec2 describe-subnets --filter "Name=cidr-block,Values=${CIDR_BLOCK}/24" --query Subnets[*].SubnetId | grep subnet- | sed 's/ //g' | sed 's/"//g'`
INTERNET_GATEWAY_ID=`aws ec2 describe-internet-gateways --filter "Name=attachment.vpc-id,Values=${VPC_ID}" --query InternetGateways[*].InternetGatewayId | grep igw- | sed 's/ //g' | sed 's/"//g'`
ROUTE_TABLE_ID=$( aws ec2 describe-route-tables --filter "Name=vpc-id,Values=${VPC_ID}" --query RouteTables[*].RouteTableId  | grep rtb- | sed 's/ //g' | sed 's/"//g' )
SECURITY_GROUP_ID=$( aws ec2 describe-security-groups --filter "Name=vpc-id,Values=${VPC_ID}" --query SecurityGroups[*].GroupId | grep sg- | sed 's/ //g' | sed 's/"//g' )
INSTANCE_ID=`aws ec2 describe-instances --filter "Name=subnet-id,Values=${SUBNET_ID}" --query Reservations[*].Instances[*].InstanceId | grep i- | sed 's/ //g' | sed 's/"//g'`

echo "delete taget ec2-instance id=${VPC_ID}"
echo "delete taget security-group id=${SECURITY_GROUP_ID}"
echo "delete taget subnet id=${SUBNET_ID}"
echo "delete taget route-table id=${ROUTE_TABLE_ID}"
echo "delete taget internet-gateway id=${INTERNET_GATEWAY_ID}"
echo "delete taget vpc id=${VPC_ID}"

# EC2 インスタンスの削除
if [ ${INSTANCE_ID} ] ; then
	aws ec2 terminate-instances --instance-ids "${INSTANCE_ID}"
	echo "deleted ec2-instances id=${SUBNET_ID}"
fi

# 非 default のセキュリティーグループの削除（default のセキュリティーグループは VPC 削除時に削除される）
#if [ "$( aws ec2 describe-security-groups --filter "Name=vpc-id,Values=${VPC_ID}" --query SecurityGroups[*].GroupId | grep sg- )" ] ; then
#	aws ec2 delete-security-group --group-id ${SECURITY_GROUP_ID}
#	echo "deleted security-group id=${SECURITY_GROUP_ID}"
#fi

# サブネットを削除する
if [ "$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${CIDR_BLOCK}/24" --query Subnets[*].SubnetId | grep subnet- )" ] ; then
	aws ec2 delete-subnet --subnet-id ${SUBNET_ID}
	echo "deleted subnet id=${SUBNET_ID}"
fi

# 非メインのルートテーブルを削除（メインルートテーブルは VPC 削除時に削除される）
#if [ "$( aws ec2 describe-route-tables --filter "Name=vpc-id,Values=${VPC_ID}" --query RouteTables[*].RouteTableId  | grep rtb- )" ] ; then
#	aws ec2 delete-route-table --route-table-id ${ROUTE_TABLE_ID}
#	echo "route-table id=${ROUTE_TABLE_ID}"
#fi

# インターネットゲートウェイを削除
if [ "$( aws ec2 describe-internet-gateways --filter "Name=attachment.vpc-id,Values=${VPC_ID}" --query InternetGateways[*].InternetGatewayId | grep igw- )" ] ; then
	aws ec2 detach-internet-gateway --internet-gateway-id ${INTERNET_GATEWAY_ID} --vpc-id ${VPC_ID}
	aws ec2 delete-internet-gateway --internet-gateway-id ${INTERNET_GATEWAY_ID}
	echo "deleted internet-gateway id=${INTERNET_GATEWAY_ID}"
fi

# VPC を削除
if [ "$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${CIDR_BLOCK}/16" --query Vpcs[*].VpcId | grep vpc- )" ] ; then
	aws ec2 delete-vpc --vpc-id ${VPC_ID}
	echo "deleted vpc id=${VPC_ID}"
fi

# EC2インスタンスを削除
