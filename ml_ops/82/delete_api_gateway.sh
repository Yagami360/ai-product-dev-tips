#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"

LAMBDA_IAM_ROLE_NAME="lambda-iam-role"
LAMBDA_FUNCTION_NAME="lambda-function"

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
# IAM role
if [ $( aws iam list-roles --query 'Roles[*].RoleName' | grep ${LAMBDA_IAM_ROLE_NAME} ) ] ; then
    aws iam detach-role-policy --role-name ${LAMBDA_IAM_ROLE_NAME} --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    aws iam delete-role --role-name ${LAMBDA_IAM_ROLE_NAME}
fi

# 関数 URL のエンドポイン
if [ $( aws lambda list-functions --query 'Functions[*].FunctionName' --output text | grep ${LAMBDA_FUNCTION_NAME} ) ] ; then
    if [ $( aws lambda list-function-url-configs --function-name ${LAMBDA_FUNCTION_NAME} --query 'FunctionUrlConfigs[*].FunctionUrl' --output text ) ] ; then
        aws lambda delete-function-url-config --function-name ${LAMBDA_FUNCTION_NAME}
    fi
fi

# Lambda 関数
if [ $( aws lambda list-functions --query 'Functions[*].FunctionName' --output text | grep ${LAMBDA_FUNCTION_NAME} ) ] ; then
    aws lambda delete-function --function-name ${LAMBDA_FUNCTION_NAME}
fi