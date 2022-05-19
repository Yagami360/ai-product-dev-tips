#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
FUNCTION_NAME="sample-function-cli"
IAM_ROLE_NAME="lambda-iam"
IAM_ROLE_FILE_PATH="lambda-iam.json"

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
<<COMMENTOUT
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

aws --version
COMMENTOUT

#-----------------------------
# Lambda 関数にアクセスするための IAM 権限を作成する
#-----------------------------
if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME}` ] ; then
    # IAM 権限の内容を定義した json ファイルから IAM 権限を作成する
    aws iam create-role \
        --role-name ${IAM_ROLE_NAME} \
        --assume-role-policy-document "file://${IAM_ROLE_FILE_PATH}"

    # 作成した IAM 権限にアクセス権限を付与する
    aws iam attach-role-policy \
        --role-name ${IAM_ROLE_NAME} \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
fi

#-----------------------------
# API コードを zip ファイルにする
#-----------------------------
zip -r app.zip app.py

#-----------------------------
# Lambda 関数を作成する
#-----------------------------
if [ `aws lambda list-functions --query 'Functions[].FunctionName' | grep ${FUNCTION_NAME}` ] ; then
    aws lambda delete-function --function-name ${FUNCTION_NAME}
fi

aws lambda create-function \
    --function-name ${FUNCTION_NAME} \
    --runtime python3.9 \
    --zip-file fileb://app.zip  \
    --handler "lambda_handler" \
    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${IAM_ROLE_NAME}

#-----------------------------
# Lambda 関数を呼び出す
#-----------------------------
aws lambda invoke \
    --invocation-type Event \
    --function-name ${FUNCTION_NAME} \
    --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
     outputfile.txt
