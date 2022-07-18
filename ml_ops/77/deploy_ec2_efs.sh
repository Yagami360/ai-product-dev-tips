#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"
ZONE="us-west-2a"

VPC_CIDR_BLOCK="10.0.0.0/16"
VPC_NAME="ec2-vpc"

EC2_SUBNET_CIDR_BLOCK="10.0.1.0/24"
EC2_SUBNET_NAME="ec2-subnet"
EC2_INTERNET_GATEWAY_NAME="ec2-internet-gateway"
EC2_ROUTE_TABLE_NAME="ec2-route-table"
EC2_SECURITY_GROUP_NAME="ec2-security-group"
EC2_INSTANCE_NAME="ec2-instance"
EC2_IMAGE_ID="ami-008b09448b998a562"		# Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
EC2_INSTANCE_TYPE="t2.micro"
EC2_SSH_KEY_NAME="ec2-key"

EFS_SECURITY_GROUP_NAME="efs-security-group"

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
sh delete_ec2_efs.sh

#=============================
# EC2インスタンス作成
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
# セキュリティグループ作成
EC2_SECURITY_GROUP_ID=$( aws ec2 create-security-group --group-name ${EC2_SECURITY_GROUP_NAME} --description "security group for efs" --vpc-id ${VPC_ID} | jq -r '.GroupId' )
echo "created security-group id=${EC2_SECURITY_GROUP_ID}"

# セキュリティグループのインバウンドルールを設定（SSH接続）
aws ec2 authorize-security-group-ingress \
	--group-id ${EC2_SECURITY_GROUP_ID} \
	--protocol tcp \
  --port 22 \
	--cidr 0.0.0.0/0
	
aws ec2 create-tags --resources ${EC2_SECURITY_GROUP_ID} --tags Key=Name,Value=${EC2_SECURITY_GROUP_NAME}

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
	--key-name ${EC2_SSH_KEY_NAME} \
	--security-group-ids ${EC2_SECURITY_GROUP_ID} \
	--subnet-id ${EC2_SUBNET_ID} > log/${EC2_INSTANCE_NAME}.json

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

#=============================
# EFS リソース作成
#=============================
#-----------------------------
# セキュリティーグループの作成
#-----------------------------
# Amazon EFS 用のセキュリティーグループを作成する
EFS_SECURITY_GROUP_ID=$( aws ec2 create-security-group --group-name ${EFS_SECURITY_GROUP_NAME} --description "security group for efs" --vpc-id ${VPC_ID} | jq -r '.GroupId' )
echo "created efs security-group id=${EFS_SECURITY_GROUP_ID}"

# セキュリティグループのインバウンドルールを設定（SSH接続）
aws ec2 authorize-security-group-ingress \
    --group-id ${EFS_SECURITY_GROUP_ID} \
    --protocol tcp \
    --port 2049 \
    --cidr 0.0.0.0/0

#　セキュリティーグループに名前をつける
aws ec2 create-tags --resources ${EFS_SECURITY_GROUP_ID} --tags Key=Name,Value=${EFS_SECURITY_GROUP_NAME}

#-----------------------------
# EFS ファイルシステムを作成する
#-----------------------------
EFS_FILE_SYSTEM_ID=$( aws efs create-file-system --creation-token TestFileSystem --tags Key=Name,Value="Test File System" | jq -r '.FileSystemId' )
echo "created efs file system id=${EFS_FILE_SYSTEM_ID}"

#【オプション】ライフサイクル管理の有効化
#aws efs put-lifecycle-configuration --file-system-id ${EFS_FILE_SYSTEM_ID} --lifecycle-policies TransitionToIA=AFTER_30_DAYS

#-----------------------------
# マウントターゲットを作成する
#-----------------------------
aws efs create-mount-target --file-system-id ${EFS_FILE_SYSTEM_ID} --subnet-id ${EC2_SUBNET_ID} --security-group ${EFS_SECURITY_GROUP_ID}
