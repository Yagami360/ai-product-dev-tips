#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"
ZONE_1="us-west-2a"
ZONE_2="us-west-2b"

VPC_CIDR_BLOCK="10.0.0.0/16"
VPC_NAME="aurora-vpc"
SUBNET_CIDR_BLOCK_1="10.0.0.0/24"
SUBNET_NAME_1="aurora-subnet-1"
SUBNET_CIDR_BLOCK_2="10.0.1.0/24"
SUBNET_NAME_2="aurora-subnet-2"
INTERNET_GATEWAY_NAME="aurora-internet-gateway"
ROUTE_TABLE_NAME_1="aurora-route-table-1"
ROUTE_TABLE_NAME_2="aurora-route-table-2"
SECURITY_GROUP_NAME="aurora-security-group"

DB_SUBNET_GROUP_NAME="aurora-db-subnet-group"
AURORA_CLUSTER_NAME="aurora-cluster"
MASTER_INSTANCE_NAME="aurora-master-instance"
REPLICA_INSTANCE_NAME="aurora-replica-instance"
DB_INSTANCE_TYPE="db.t2.micro"

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
sh delete_aurora.sh

#=============================
# リソース作成
#=============================
mkdir -p log

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

# DNS ホスト名を有効化
aws ec2 modify-vpc-attribute --vpc-id ${VPC_ID} --enable-dns-hostnames

#-----------------------------
# サブネット１を作成する
#-----------------------------
# サブネットマスクを作成
aws ec2 create-subnet \
	--vpc-id ${VPC_ID} \
	--cidr-block ${SUBNET_CIDR_BLOCK_1} \
	--availability-zone ${ZONE_1} > log/${SUBNET_NAME_1}.json

# サブネット ID を取得
SUBNET_ID_1=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${SUBNET_CIDR_BLOCK_1}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
echo "created ec2 subnet id=${SUBNET_ID_1}"

# サブネットに名前をつける
aws ec2 create-tags --resources ${SUBNET_ID_1} --tags Key=Name,Value=${SUBNET_NAME_1}

#-----------------------------
# サブネット２を作成する
#-----------------------------
# サブネットマスクを作成
aws ec2 create-subnet \
	--vpc-id ${VPC_ID} \
	--cidr-block ${SUBNET_CIDR_BLOCK_2} \
	--availability-zone ${ZONE_2} > log/${SUBNET_NAME_2}.json

# サブネット ID を取得
SUBNET_ID_2=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${SUBNET_CIDR_BLOCK_2}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
echo "created ec2 subnet id=${SUBNET_ID_2}"

# サブネットに名前をつける
aws ec2 create-tags --resources ${SUBNET_ID_2} --tags Key=Name,Value=${SUBNET_NAME_2}

#-----------------------------
# インターネットゲートウェイの作成
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
# ルートテーブル１を作成する
#-----------------------------
# ルートテーブルの作成＆ルートテーブルID取得
ROUTE_TABLE_ID_1=$( aws ec2 create-route-table --vpc-id ${VPC_ID} | jq -r '.RouteTable.RouteTableId' )
echo "created route-table id=${ROUTE_TABLE_ID_1}"

# ルートテーブルの名前を設定
aws ec2 create-tags --resources ${ROUTE_TABLE_ID_1} --tags Key=Name,Value=${ROUTE_TABLE_NAME_1}

# ルート（ルートテーブルの各要素でインターネットネットゲートウェイとの紐付け情報）を作成
aws ec2 create-route \
    --route-table-id ${ROUTE_TABLE_ID_1} \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id ${INTERNET_GATEWAY_ID}

# ルートをサブネットに紐付け
aws ec2 associate-route-table \
    --route-table-id ${ROUTE_TABLE_ID_1} \
    --subnet-id ${SUBNET_ID_1}

#-----------------------------
# ルートテーブル２を作成する
#-----------------------------
# ルートテーブルの作成＆ルートテーブルID取得
ROUTE_TABLE_ID_2=$( aws ec2 create-route-table --vpc-id ${VPC_ID} | jq -r '.RouteTable.RouteTableId' )
echo "created route-table id=${ROUTE_TABLE_ID_2}"

# ルートテーブルの名前を設定
aws ec2 create-tags --resources ${ROUTE_TABLE_ID_2} --tags Key=Name,Value=${ROUTE_TABLE_NAME_2}

# ルート（ルートテーブルの各要素でインターネットネットゲートウェイとの紐付け情報）を作成
aws ec2 create-route \
    --route-table-id ${ROUTE_TABLE_ID_2} \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id ${INTERNET_GATEWAY_ID}

# ルートをサブネットに紐付け
aws ec2 associate-route-table \
    --route-table-id ${ROUTE_TABLE_ID_2} \
    --subnet-id ${SUBNET_ID_2}

#-----------------------------
# セキュリティーグループの作成
#-----------------------------
# セキュリティグループ作成
SECURITY_GROUP_ID=$( aws ec2 create-security-group --group-name ${SECURITY_GROUP_NAME} --description "security group for efs" --vpc-id ${VPC_ID} | jq -r '.GroupId' )
echo "created security-group id=${SECURITY_GROUP_ID}"

# セキュリティグループのインバウンドルールを設定（SSH接続）
aws ec2 authorize-security-group-ingress \
	--group-id ${SECURITY_GROUP_ID} \
	--protocol tcp \
    --port 3306 \
	--cidr 0.0.0.0/0 > log/${SECURITY_GROUP_NAME}.json
	
aws ec2 create-tags --resources ${SECURITY_GROUP_ID} --tags Key=Name,Value=${SECURITY_GROUP_NAME}

#-----------------------------
# DB サブネットグループを作成する
#-----------------------------
aws rds create-db-subnet-group \
    --db-subnet-group-name ${DB_SUBNET_GROUP_NAME} \
    --db-subnet-group-description "aurora mysql subnet group" \
    --subnet-ids "${SUBNET_ID_1}" "${SUBNET_ID_2}" > log/${DB_SUBNET_GROUP_NAME}.json

#-----------------------------
# クラスター作成
#-----------------------------
aws rds create-db-cluster \
    --db-cluster-identifier ${AURORA_CLUSTER_NAME} \
    --engine aurora-mysql \
    --engine-version 8.0 \
    --master-username admin \
    --master-user-password 12345678 \
    --db-subnet-group-name ${DB_SUBNET_GROUP_NAME} \
    --vpc-security-group-ids ${SECURITY_GROUP_ID} \
    --availability-zones ${ZONE_1} > log/${AURORA_CLUSTER_NAME}.json

#    --port 3306 \
#    --database-name aurora-mysql-database

#-----------------------------
# マスターインスタンス
#-----------------------------
aws rds create-db-instance \
    --db-cluster-identifier ${AURORA_CLUSTER_NAME} \
    --db-instance-identifier ${MASTER_INSTANCE_NAME} \
    --db-subnet-group-name ${DB_SUBNET_GROUP_NAME} \
    --db-instance-class ${DB_INSTANCE_TYPE} \
    --availability-zone ${ZONE_1} \
    --engine aurora-mysql \
    --engine-version 8.0 \
    --publicly-accessible

#    --monitoring-interval 60 \
#    --monitoring-role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/rds-monitoring-role \
#    --auto-minor-version-upgrade \
#    --enable-performance-insights

#    --no-publicly-accessible \
#    --db-parameter-group-name sample-instance-parameter \