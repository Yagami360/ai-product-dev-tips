#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"
ZONE="us-west-2a"

IAM_ROLE_NAME="elasticache-iam-role"
IAM_POLICY_FILE_PATH="elasticache-iam-policy.json"

VPC_CIDR_BLOCK="10.10.0.0/16"
VPC_NAME="elasticache-vpc"

CACHE_SUBNET_CIDR_BLOCK="10.10.0.0/24"
CACHE_SUBNET_NAME="elasticache-cluster-subnet"
CACHE_SECURITY_GROUP_NAME="elasticache-cluster-security-group"
CACHE_SUBNET_GROUP_NAME="elasticache-subnet-group"
CACHE_PARAMETER_GROUP_NAME="elasticache-redis-parameter-group"
CACHE_CLUSTER_NAME="elasticache-redis-cluster"

EC2_SUBNET_CIDR_BLOCK="10.10.0.0/32"
EC2_SUBNET_NAME="elasticache-ec2-subnet"
EC2_INTERNET_GATEWAY_NAME="elasticache-ec2-internet-gateway"
EC2_ROUTE_TABLE_NAME="elasticache-ec2-route-table"
EC2_SECURITY_GROUP_NAME="elasticache-ec2-security-group"
EC2_INSTANCE_NAME="elasticache-ec2-instance"
EC2_IMAGE_ID="ami-008b09448b998a562"		# Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
EC2_INSTANCE_TYPE="t2.micro"
EC2_SSH_KEY_NAME="ec2-key"

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

# セキュリティグループのインバウンドルールを設定
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

#=============================
# EC2インスタンス作成
#=============================
#-----------------------------
# VPC を作成する
#-----------------------------
# キャッシュクラスターと同じ VPC を使用するのでパス

#-----------------------------
# サブネットを作成する
#-----------------------------
# サブネットマスクを作成
aws ec2 create-subnet \
	--vpc-id ${VPC_ID} \
	--cidr-block ${EC2_SUBNET_CIDR_BLOCK} \
	--availability-zone ${ZONE} > log/${EC2_SUBNET_NAME}.json

# サブネット ID を取得
EC2_SUBNET_ID=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${EC2_SUBNET_CIDR_BLOCK}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
echo "created ec2 subnet id=${EC2_SUBNET_ID}"

# サブネットに名前をつける
aws ec2 create-tags --resources ${EC2_SUBNET_ID} --tags Key=Name,Value=${EC2_SUBNET_NAME}

#-----------------------------
# インターネットゲートウェイを作成する
#-----------------------------
# インターネットゲートウェイの作成＆インターネットゲートウェイID取得
EC2_INTERNET_GATEWAY_ID=$( aws ec2 create-internet-gateway | jq -r '.InternetGateway.InternetGatewayId' )
echo "created internet-gateway id=${EC2_INTERNET_GATEWAY_ID}"

# インターネットゲートウェイの名前を設定
aws ec2 create-tags --resources ${EC2_INTERNET_GATEWAY_ID} --tags Key=Name,Value=${EC2_INTERNET_GATEWAY_NAME}

# 作成したインターネットゲートウェイに VPC を紐付けする
aws ec2 attach-internet-gateway \
    --internet-gateway-id ${EC2_INTERNET_GATEWAY_ID} \
    --vpc-id ${VPC_ID}

#-----------------------------
# ルートテーブルを作成する
#-----------------------------
# ルートテーブルの作成＆ルートテーブルID取得
EC2_ROUTE_TABLE_ID=$( aws ec2 create-route-table --vpc-id ${VPC_ID} | jq -r '.RouteTable.RouteTableId' )
echo "created route-table id=${EC2_ROUTE_TABLE_ID}"

# ルートテーブルの名前を設定
aws ec2 create-tags --resources ${EC2_ROUTE_TABLE_ID} --tags Key=Name,Value=${EC2_ROUTE_TABLE_NAME}

# ルート（ルートテーブルの各要素でインターネットネットゲートウェイとの紐付け情報）を作成
aws ec2 create-route \
	--route-table-id ${EC2_ROUTE_TABLE_ID} \
	--destination-cidr-block 0.0.0.0/0 \
	--gateway-id ${EC2_INTERNET_GATEWAY_ID}

# ルートをサブネットに紐付け
aws ec2 associate-route-table \
	--route-table-id ${EC2_ROUTE_TABLE_ID} \
    --subnet-id ${EC2_SUBNET_ID}

#-----------------------------
# セキュリティーグループの作成
#-----------------------------
# キャッシュクラスターと同じセキュリティーグループを使用するのでパス

#-----------------------------
# SSH 鍵の登録
#-----------------------------
if [ ! "${HOME}/.ssh/${EC2_SSH_KEY_NAME}.pem" ] ; then
	aws ec2 create-key-pair --key-name ${EC2_SSH_KEY_NAME} --query 'KeyMaterial' --output text > "${HOME}/.ssh/${EC2_SSH_KEY_NAME}.pem"
	chmod 400 "${HOME}/.ssh/${EC2_SSH_KEY_NAME}.pem"
fi

#-----------------------------
# EC2 インスタンスの作成
#-----------------------------
# サブネット内の EC2 インスタンスにパブリックIPアドレスを自動的に割り当て
aws ec2 modify-subnet-attribute \
	--subnet-id ${EC2_SUBNET_ID} \
	--map-public-ip-on-launch

# EC2 インスタンスの作成
aws ec2 run-instances \
	--image-id ${EC2_IMAGE_ID} \
	--instance-type ${EC2_INSTANCE_TYPE} \
	--count 1 \
	--key-name ${SSH_KEY_NAME} \
	--security-group-ids ${SECURITY_GROUP_ID} \
	--subnet-id ${EC2_SUBNET_ID}

# インスタンスIDを取得
EC2_INSTANCE_ID=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID}" --query Reservations[*].Instances[*].InstanceId --output text | grep i- )
echo "created ec2-instance id=${EC2_INSTANCE_ID}"

# インスタンスの名前を設定
aws ec2 create-tags --resources ${EC2_INSTANCE_ID} --tags Key=Name,Value=${EC2_INSTANCE_NAME}

#-----------------------------
# EC2 インスタンスに接続する
#-----------------------------
#IP_ADDRESS=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID}" --query Reservations[*].Instances[*].PublicIpAddress --output text )
#echo "ec2-instance ip=${IP_ADDRESS}"
#ssh -i "${HOME}/.ssh/${EC2_SSH_KEY_NAME}.pem" ubuntu@${IP_ADDRESS}
