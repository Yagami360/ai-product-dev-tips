#!/bin/sh
set -eu
REGION="us-west-2"
ZONE="us-west-2a"

CIDR_BLOCK=10.10.0.0
VPC_NAME="datadog-ec2-vpc"
SUBNET_NAME="datadog-ec2-subnet"

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
# EC2 リソースを削除する
#（各種リソースが関連付けられているので作成順の逆に削除）
#-----------------------------
VPC_ID=`aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${CIDR_BLOCK}/16" --query Vpcs[*].VpcId | grep vpc- | sed 's/ //g' | sed 's/"//g'`
SUBNET_ID=`aws ec2 describe-subnets --filter "Name=cidr-block,Values=${CIDR_BLOCK}/24" --query Subnets[*].SubnetId | grep subnet- | sed 's/ //g' | sed 's/"//g'`
#INTERNET_GATEWAY_ID=`aws ec2 describe-internet-gateways --filter "Name=VpcId,Values=${VPC_ID}" --query InternetGateways[*].InternetGatewayId | grep igw- | sed 's/ //g' | sed 's/"//g'`

# インターネットゲートウェイを削除
#if [ "$( aws ec2 describe-internet-gateways --filter "Name=VpcId,Values=${VPC_ID}" --query InternetGateways[*].InternetGatewayId | grep igw- )" ] ; then
#	aws ec2 delete-internet-gateway --internet-gateway-id ${INTERNET_GATEWAY_ID}
#fi

# サブネットを削除する
if [ "$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${CIDR_BLOCK}/24" --query Subnets[*].SubnetId | grep subnet- )" ] ; then
	aws ec2 delete-subnet --subnet-id ${SUBNET_ID}
fi

# VPC を削除
if [ "$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${CIDR_BLOCK}/16" --query Vpcs[*].VpcId | grep vpc- )" ] ; then
	aws ec2 delete-vpc --vpc-id ${VPC_ID}
fi

#-----------------------------
# VPC を作成する
#-----------------------------
# VPC を作成
aws ec2 create-vpc --cidr-block ${CIDR_BLOCK}/16

# 作成した VPC の VPC ID 取得
VPC_ID=`aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${CIDR_BLOCK}/16" --query Vpcs[*].VpcId | grep vpc- | sed 's/ //g' | sed 's/"//g'`
echo "VPC_ID : ${VPC_ID}"

# VPC に名前をつける
aws ec2 create-tags --resources ${VPC_ID} --tags Key=Name,Value=${VPC_NAME}

#-----------------------------
# サブネットを作成する
#-----------------------------
# サブネットマスクを作成
aws ec2 create-subnet \
	--vpc-id ${VPC_ID} \
	--cidr-block ${CIDR_BLOCK}/24 \
	--availability-zone ${ZONE}

# サブネット ID を取得
SUBNET_ID=`aws ec2 describe-subnets --filter "Name=cidr-block,Values=${CIDR_BLOCK}/24" --query Subnets[*].SubnetId | grep subnet- | sed 's/ //g' | sed 's/"//g'`
echo "SUBNET_ID : ${SUBNET_ID}"

# サブネットに名前をつける
aws ec2 create-tags --resources ${SUBNET_ID} --tags Key=Name,Value=${SUBNET_NAME}

#-----------------------------
# インターネットゲートウェイを作成する
#-----------------------------
# インターネットゲートウェイの作成
aws ec2 create-internet-gateway

# インターネットゲートウェイID取得
INTERNET_GATEWAY_ID=`aws ec2 describe-internet-gateways --filter "Name=VpcId,Values=${VPC_ID}" --query InternetGateways[*].InternetGatewayId | grep igw- | sed 's/ //g' | sed 's/"//g'`

# 作成したインターネットゲートウェイに VPC をアタッチする
aws ec2 attach-internet-gateway 
    --internet-gateway-id ${INTERNET_GATEWAY_ID} \
    --vpc-id ${VPC_ID}
