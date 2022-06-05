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
SSH_KEY_NAME="key.pem"

IMAGE_ID="ami-00f045aed21a55240"
INSTANCE_TYPE="t2.micro"

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
#ROUTE_TABLE_ID=$( aws ec2 describe-route-tables --filter "Name=vpc-id,Values=${VPC_ID}" --query RouteTables[*].RouteTableId  | grep rtb- | sed 's/ //g' | sed 's/"//g' )
#SECURITY_GROUP_ID=$( aws ec2 describe-security-groups --filter "Name=vpc-id,Values=${VPC_ID}" --query SecurityGroups[*].GroupId | grep sg- | sed 's/ //g' | sed 's/"//g' )

# セキュリティーグループの削除

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

#-----------------------------
# VPC を作成する
#-----------------------------
# VPC を作成
aws ec2 create-vpc --cidr-block ${CIDR_BLOCK}/16

# 作成した VPC の VPC ID 取得
VPC_ID=`aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${CIDR_BLOCK}/16" --query Vpcs[*].VpcId | grep vpc- | sed 's/ //g' | sed 's/"//g'`
echo "created vpc id=${VPC_ID}"

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
echo "created subnet id=${SUBNET_ID}"

# サブネットに名前をつける
aws ec2 create-tags --resources ${SUBNET_ID} --tags Key=Name,Value=${SUBNET_NAME}

#-----------------------------
# インターネットゲートウェイを作成する
#-----------------------------
# インターネットゲートウェイの作成＆インターネットゲートウェイID取得
INTERNET_GATEWAY_ID=$( aws ec2 create-internet-gateway | jq -r '.InternetGateway.InternetGatewayId' )
echo "created internet-gateway id=${INTERNET_GATEWAY_ID}"

# インターネットゲートウェイの名前を設定
aws ec2 create-tags --resources ${INTERNET_GATEWAY_ID} --tags Key=Name,Value=${INTERNET_GATEWAY_NAME}

# 作成したインターネットゲートウェイに VPC を紐付けする
aws ec2 attach-internet-gateway \
    --internet-gateway-id ${INTERNET_GATEWAY_ID} \
    --vpc-id ${VPC_ID}

#-----------------------------
# ルートテーブルを作成する
#-----------------------------
# ルートテーブルの作成
#aws ec2 create-route-table --vpc-id ${VPC_ID}

# ルートテーブルID取得
#ROUTE_TABLE_ID=$( aws ec2 describe-route-tables --filter "Name=vpc-id,Values=${VPC_ID}" --query RouteTables[*].RouteTableId  | grep rtb- | sed 's/ //g' | sed 's/"//g' )

# ルートテーブルの作成＆ルートテーブルID取得
ROUTE_TABLE_ID=$( aws ec2 create-route-table --vpc-id ${VPC_ID} | jq -r '.RouteTable.RouteTableId' )
echo "created route-table id=${ROUTE_TABLE_ID}"

# ルートテーブルの名前を設定
aws ec2 create-tags --resources ${ROUTE_TABLE_ID} --tags Key=Name,Value=${ROUTE_TABLE_NAME}

# ルート（ルートテーブルの各要素でインターネットネットゲートウェイとの紐付け情報）を作成
aws ec2 create-route \
	--route-table-id ${ROUTE_TABLE_ID} \
	--destination-cidr-block 0.0.0.0/0 \
	--gateway-id ${INTERNET_GATEWAY_ID}

# ルートをサブネットに紐付け
aws ec2 associate-route-table \
	--route-table-id ${ROUTE_TABLE_ID} \
    --subnet-id ${SUBNET_ID}

#-----------------------------
# セキュリティーグループの作成
#-----------------------------
# セキュリティーグループの作成
#aws ec2 create-security-group \
#	--group-name ${SECURITY_GROUP_NAME} \
#	--description "security group for ec2 instance" \
#	--vpc-id ${VPC_ID}

# セキュリティグループIDを取得
#SECURITY_GROUP_ID=$( aws ec2 describe-security-groups --filter "Name=vpc-id,Values=${VPC_ID}" --query SecurityGroups[*].GroupId | grep sg- | sed 's/ //g' | sed 's/"//g' )

# セキュリティーグループの作成＆セキュリティグループIDを取得
SECURITY_GROUP_ID=$( aws ec2 create-security-group --group-name ${SECURITY_GROUP_NAME} --description "security group for ec2 instance" --vpc-id ${VPC_ID} | jq -r '.GroupId' )
echo "created security-group id=${SECURITY_GROUP_ID}"

# セキュリティグループのインバウンドルールを設定
aws ec2 authorize-security-group-ingress \
	--group-id ${SECURITY_GROUP_ID} \
    --protocol tcp \
	--port 22 \
	--cidr 0.0.0.0/0

#-----------------------------
# SSH 鍵の登録
#-----------------------------
if [ ! ${HOME}/.ssh/${SSH_KEY_NAME} ] ; then
	aws ec2 create-key-pair --key-name ${SSH_KEY_NAME} --query 'KeyMaterial' --output text > ${HOME}/.ssh/${SSH_KEY_NAME}
	chmod 400 ${HOME}/.ssh/${SSH_KEY_NAME}
fi

#-----------------------------
# EC2 インスタンスの作成
#-----------------------------
# サブネット内の EC2 インスタンスにパブリックIPアドレスを自動的に割り当て
aws ec2 modify-subnet-attribute \
	--subnet-id ${SUBNET_ID} \
	--map-public-ip-on-launch

# EC2 インスタンスの作成
aws ec2 run-instances \
	--image-id ${IMAGE_ID} \ 
	--instance-type ${INSTANCE_TYPE} \
	--count 1 \
	--key-name ${HOME}/.ssh/${SSH_KEY_NAME} \
	--security-group-ids ${SECURITY_GROUP_ID} \
	--subnet-id ${SUBNET_ID}

# インスタンスIDを取得
INSTANCE_ID=""

# インスタンスの名前を設定
aws ec2 create-tags --resources ${INSTANCE_ID} --tags Key=Name,Value=${INSTANCE_ID}

#-----------------------------
# EC2 インスタンスに接続する
#-----------------------------
ssh -i ${HOME}/.ssh/${SSH_KEY_NAME} ec2-user@${INSTANCE_ID}
