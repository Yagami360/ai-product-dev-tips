#!/bin/sh
#set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"

VPC_CIDR_BLOCK="10.0.0.0/16"
EC2_SUBNET_CIDR_BLOCK="10.0.1.0/24"
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
VPC_ID=$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${VPC_CIDR_BLOCK}" --query Vpcs[*].VpcId --output text | grep "vpc-" )
EC2_SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${EC2_SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep subnet- )
EC2_INTERNET_GATEWAY_ID=$( aws ec2 describe-internet-gateways --filter "Name=attachment.vpc-id,Values=${VPC_ID}" --query InternetGateways[*].InternetGatewayId --output text | grep igw- )
EC2_ROUTE_TABLE_ID=$( aws ec2 describe-route-tables --filter "Name=vpc-id,Values=${VPC_ID}" --query RouteTables[*].RouteTableId --output text | grep rtb- )
EC2_INSTANCE_ID=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID}" --query Reservations[*].Instances[*].InstanceId --output text | grep i- )

# EC2 インスタンスの削除
if [ ${EC2_INSTANCE_ID} ] ; then
	aws ec2 terminate-instances --instance-ids "${EC2_INSTANCE_ID}"
	echo "deleted ec2-instances id=${EC2_INSTANCE_ID}"
fi

# 非メインのルートテーブルを削除（メインルートテーブルは VPC 削除時に削除される）
if [ ${EC2_ROUTE_TABLE_ID} ] ; then
	aws ec2 delete-route-table --route-table-id ${EC2_ROUTE_TABLE_ID}
	echo "deleted route-table id=${EC2_ROUTE_TABLE_ID}"
fi

# インターネットゲートウェイを削除
if [ ${EC2_INTERNET_GATEWAY_ID} ] ; then
	aws ec2 detach-internet-gateway --internet-gateway-id ${EC2_INTERNET_GATEWAY_ID} --vpc-id ${VPC_ID}
	aws ec2 delete-internet-gateway --internet-gateway-id ${EC2_INTERNET_GATEWAY_ID}
	echo "deleted internet-gateway id=${EC2_INTERNET_GATEWAY_ID}"
fi

# サブネットを削除する
if [ ${EC2_SUBNET_ID} ] ; then
	aws ec2 delete-subnet --subnet-id ${EC2_SUBNET_ID}
	echo "deleted subnet id=${EC2_SUBNET_ID}"
fi

# VPC
#VPC_ID=$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${VPC_CIDR_BLOCK}" --query Vpcs[*].VpcId --output text | grep "vpc-" )
#if [ ${VPC_ID} ] ; then
#	aws ec2 delete-vpc --vpc-id ${VPC_ID}
#	echo "deleted vpc id=${VPC_ID}"
#	sleep 10
#fi
