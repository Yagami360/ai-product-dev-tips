#!/bin/sh
#set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"

VPC_CIDR_BLOCK="10.0.0.0/16"
SUBNET_CIDR_BLOCK_1="10.0.0.0/24"
SUBNET_CIDR_BLOCK_2="10.0.1.0/24"

DB_SUBNET_GROUP_NAME="aurora-db-subnet-group"
AURORA_CLUSTER_NAME="aurora-cluster"

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

VPC_ID=$( aws ec2 describe-vpcs --filter "Name=cidr-block,Values=${VPC_CIDR_BLOCK}" --query Vpcs[*].VpcId --output text | grep "vpc-" )
SUBNET_ID_1=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${SUBNET_CIDR_BLOCK_1}" --query Subnets[*].SubnetId --output text | grep subnet- )
SUBNET_ID_2=$( aws ec2 describe-subnets --filter "Name=cidr-block,Values=${SUBNET_CIDR_BLOCK_2}" --query Subnets[*].SubnetId --output text | grep subnet- )
SECURITY_GROUP_ID=$( aws ec2 describe-security-groups --filter "Name=vpc-id,Values=${VPC_ID}" --query SecurityGroups[0].GroupId --output text | grep sg- )
echo "VPC_ID : ${VPC_ID}"
echo "SUBNET_ID_1 : ${SUBNET_ID_1}"
echo "SUBNET_ID_2 : ${SUBNET_ID_2}"
echo "SECURITY_GROUP_ID : ${SECURITY_GROUP_ID}"

# Aurora クラスター
if [ $( aws rds describe-db-clusters --query DBClusters[*].DBClusterIdentifier --output text | grep ${AURORA_CLUSTER_NAME} ) ] ; then
	aws rds delete-db-cluster --db-cluster-identifier ${AURORA_CLUSTER_NAME}
	sleep 30

	for i in `seq 300`
	do
		STATUS=$( aws rds describe-db-clusters --query DBClusters[*].Status --output text )
		if [ ${STATUS} = "deleting" ] ; then
			echo "deleting ${AURORA_CLUSTER_NAME} ..."
			sleep 5
	else
			break
		fi
	done
	echo "deleted ${AURORA_CLUSTER_NAME}"
fi

# DB サブネットグループ
if [ $( aws rds describe-db-subnet-groups --query DBSubnetGroups[*].DBSubnetGroupName --output text | grep ${DB_SUBNET_GROUP_NAME} ) ] ; then
	aws rds delete-db-subnet-group --db-subnet-group-name ${DB_SUBNET_GROUP_NAME}
fi

# セキュリティーグループ
if [ ${SECURITY_GROUP_ID} ] ; then
	aws ec2 delete-security-group --group-id ${SECURITY_GROUP_ID}
	echo "deleted security-group id=${SECURITY_GROUP_ID}"
fi

# サブネットを削除する
if [ ${SUBNET_ID_1} ] ; then
	aws ec2 delete-subnet --subnet-id ${SUBNET_ID_1}
	echo "deleted subnet id=${SUBNET_ID_1}"
fi

if [ ${SUBNET_ID_2} ] ; then
	aws ec2 delete-subnet --subnet-id ${SUBNET_ID_2}
	echo "deleted subnet id=${SUBNET_ID_2}"
fi

# VPC
if [ ${VPC_ID} ] ; then
	aws ec2 delete-vpc --vpc-id ${VPC_ID}
	echo "deleted vpc id=${VPC_ID}"
	sleep 10
fi
