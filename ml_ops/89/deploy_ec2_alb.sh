#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
AWS_REGION=us-west-2
ZONE_1="us-west-2a"
ZONE_2="us-west-2b"

VPC_CIDR_BLOCK="10.0.0.0/16"
VPC_NAME="ec2-vpc"

EC2_SUBNET_CIDR_BLOCK_1="10.0.0.0/24"
EC2_SUBNET_NAME_1="ec2-subnet-1"
EC2_SUBNET_CIDR_BLOCK_2="10.0.1.0/24"
EC2_SUBNET_NAME_2="ec2-subnet-2"

EC2_INTERNET_GATEWAY_NAME="ec2-internet-gateway"
EC2_ROUTE_TABLE_NAME="ec2-route-table"
EC2_SECURITY_GROUP_NAME="ec2-security-group"

EC2_INSTANCE_NAME_1="ec2-instance-1"
EC2_IMAGE_ID_1="ami-008b09448b998a562"		# Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
EC2_INSTANCE_TYPE_1="t2.micro"
EC2_INSTANCE_NAME_2="ec2-instance-2"
EC2_IMAGE_ID_2="ami-008b09448b998a562"
EC2_INSTANCE_TYPE_2="t2.micro"

EC2_SSH_KEY_NAME="ec2-key"

ALB_NAME="alb-ec2"
ALB_TARGET_GROUP_NAME="alb-taget-group"

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
# AWS デフォルト値の設定
#=============================
# プロファイル作成 
if [ ! $( aws configure list-profiles | grep ${AWS_PROFILE} ) ] ; then
    aws configure --profile ${AWS_PROFILE}
fi
aws configure list

# AWS CLI を設定する環境変数
export AWS_ACCOUNTID=${AWS_ACCOUNT_ID}
export AWS_PROFILE=${AWS_PROFILE}
export AWS_DEFAULT_REGION=${AWS_REGION}

cat ~/.aws/config
cat ~/.aws/credentials

#=============================
# 各種 AWS リソース削除
#=============================
#sh delete_ec2_alb.sh

#=============================
# EC2 関連のリソース作成
#=============================
mkdir -p logs

#-----------------------------
# VPC を作成する
#-----------------------------
# VPC を作成
aws ec2 create-vpc --cidr-block ${VPC_CIDR_BLOCK} > logs/${VPC_NAME}.json

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
	--cidr-block ${EC2_SUBNET_CIDR_BLOCK_1} \
	--availability-zone ${ZONE_1} > logs/${EC2_SUBNET_NAME_1}.json

# サブネット ID を取得
EC2_SUBNET_ID_1=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${EC2_SUBNET_CIDR_BLOCK_1}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
echo "created ec2 subnet id=${EC2_SUBNET_ID_1}"

# サブネットに名前をつける
aws ec2 create-tags --resources ${EC2_SUBNET_ID_1} --tags Key=Name,Value=${EC2_SUBNET_NAME_1}

#-----------------------------
# サブネット２を作成する
#-----------------------------
# サブネットマスクを作成
aws ec2 create-subnet \
	--vpc-id ${VPC_ID} \
	--cidr-block ${EC2_SUBNET_CIDR_BLOCK_2} \
	--availability-zone ${ZONE_2} > logs/${EC2_SUBNET_NAME_2}.json

# サブネット ID を取得
EC2_SUBNET_ID_2=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${EC2_SUBNET_CIDR_BLOCK_2}" --query Subnets[*].SubnetId --output text | grep "subnet-" )
echo "created ec2 subnet id=${EC2_SUBNET_ID_2}"

# サブネットに名前をつける
aws ec2 create-tags --resources ${EC2_SUBNET_ID_2} --tags Key=Name,Value=${EC2_SUBNET_NAME_2}

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
    --subnet-id ${EC2_SUBNET_ID_1}

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
	
# セキュリティグループのインバウンドルールを設定（HTTP接続）
aws ec2 authorize-security-group-ingress \
	--group-id ${EC2_SECURITY_GROUP_ID} \
	--protocol tcp \
	--port 80 \
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
# EC2 インスタンス１の作成
#-----------------------------
# サブネット内の EC2 インスタンスにパブリックIPアドレスを自動的に割り当て
aws ec2 modify-subnet-attribute \
	--subnet-id ${EC2_SUBNET_ID_1} \
	--map-public-ip-on-launch

# EC2 インスタンスの作成
aws ec2 run-instances \
	--image-id ${EC2_IMAGE_ID_1} \
	--instance-type ${EC2_INSTANCE_TYPE_1} \
	--count 1 \
	--key-name ${EC2_SSH_KEY_NAME} \
	--security-group-ids ${EC2_SECURITY_GROUP_ID} \
	--subnet-id ${EC2_SUBNET_ID_1} > logs/${EC2_INSTANCE_NAME_1}.json

# インスタンスIDを取得
EC2_INSTANCE_ID_1=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID_1}" --query Reservations[*].Instances[*].InstanceId --output text | grep i- )
echo "created ec2-instance id=${EC2_INSTANCE_ID_1}"

# インスタンスの名前を設定
aws ec2 create-tags --resources ${EC2_INSTANCE_ID_1} --tags Key=Name,Value=${EC2_INSTANCE_NAME_1}

#-----------------------------
# EC2 インスタンス２の作成
#-----------------------------
# サブネット内の EC2 インスタンスにパブリックIPアドレスを自動的に割り当て
#aws ec2 modify-subnet-attribute \
#	--subnet-id ${EC2_SUBNET_ID_2} \
#	--map-public-ip-on-launch

# EC2 インスタンスの作成
aws ec2 run-instances \
	--image-id ${EC2_IMAGE_ID_2} \
	--instance-type ${EC2_INSTANCE_TYPE_2} \
	--count 1 \
	--key-name ${EC2_SSH_KEY_NAME} \
	--security-group-ids ${EC2_SECURITY_GROUP_ID} \
	--subnet-id ${EC2_SUBNET_ID_2} > logs/${EC2_INSTANCE_NAME_2}.json

# インスタンスIDを取得
EC2_INSTANCE_ID_2=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID_2}" --query Reservations[*].Instances[*].InstanceId --output text | grep i- )
echo "created ec2-instance id=${EC2_INSTANCE_ID_2}"

# インスタンスの名前を設定
aws ec2 create-tags --resources ${EC2_INSTANCE_ID_2} --tags Key=Name,Value=${EC2_INSTANCE_NAME_2}

#-----------------------------
# EC2 インスタンスに接続する
#-----------------------------
#IP_ADDRESS=$( aws ec2 describe-instances --filter "Name=subnet-id,Values=${EC2_SUBNET_ID}" --query Reservations[*].Instances[*].PublicIpAddress --output text )
#echo "ec2-instance ip=${IP_ADDRESS}"
#ssh -i "${HOME}/.ssh/${EC2_SSH_KEY_NAME}.pem" ubuntu@${IP_ADDRESS}

#=============================
# ALB 関連のリソース作成
#=============================
# ALB [Application Load Balancer] を作成する
aws elbv2 create-load-balancer \
	--name ${ALB_NAME} \
	--subnets ${EC2_SUBNET_ID_1} ${EC2_SUBNET_ID_2} \
	--security-groups ${EC2_SECURITY_GROUP_ID} > logs/${ALB_NAME}.json

ALB_ARN=$( aws elbv2 describe-load-balancers --query LoadBalancers[0].LoadBalancerArn --output text )

# ターゲットグループを作成する
aws elbv2 create-target-group \
	--name ${ALB_TARGET_GROUP_NAME} \
	--protocol HTTP --port 80 \
	--vpc-id ${VPC_ID} > logs/${ALB_TARGET_GROUP_NAME}.json

ALB_TARGET_GROUP_ARN=$( aws elbv2 describe-target-groups --query TargetGroups[0].TargetGroupArn --output text )

# ターゲットグループに EC2 インスタンスを登録する
aws elbv2 register-targets \
	--target-group-arn ${ALB_TARGET_GROUP_ARN} \
	--targets Id=${EC2_INSTANCE_ID_1},Port=80 Id=${EC2_INSTANCE_ID_2},Port=80

# リスナー（ALBとターゲットグループの紐付け）を作成する
aws elbv2 create-listener \
	--load-balancer-arn ${ALB_ARN} \
	--protocol HTTP --port 80 \
	--default-actions Type=forward,TargetGroupArn=${ALB_TARGET_GROUP_ARN} > logs/${ALB_NAME}_listener.json

# ターゲットグループに登録されている EC2 インスタンスの状態が healthy になっていることを確認する
aws elbv2 describe-target-health --target-group-arn ${ALB_TARGET_GROUP_ARN}