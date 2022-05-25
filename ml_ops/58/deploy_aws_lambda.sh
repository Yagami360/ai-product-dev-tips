#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
IAM_ROLE_NAME="lambda-iam-role"
IAM_POLICY_FILE_PATH="lambda-iam-policy.json"
FUNCTION_NAME="lambda-function-cli"

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
aws --version

#-----------------------------
# Lambda 関数実行のための IAM を作成する
#-----------------------------
#if [ `aws iam list-roles --query 'Roles[].RoleName' | grep -x ${IAM_ROLE_NAME}` ] ; then
#    aws iam delete-role --role-name ${IAM_ROLE_NAME}
#fi

if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep -x ${IAM_ROLE_NAME}` ] ; then
    # Lambda 関数実行のための IAM ロールを作成する
    aws iam create-role \
        --role-name ${IAM_ROLE_NAME} \
        --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH}" &

    sleep 10

    # 作成した IAM ロールに、Lambda サービスにアクセスできるようにするための IAM ポリシーを付与する
    aws iam attach-role-policy \
        --role-name ${IAM_ROLE_NAME} \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
fi

#-----------------------------
# API コードを zip ファイルにする
#-----------------------------
zip -r lambda_function.zip lambda_function.py

#-----------------------------
# Lambda 関数を作成する
#-----------------------------
# Lambda 関数を作成
if [ `aws lambda list-functions --query 'Functions[].FunctionName' | grep -x ${FUNCTION_NAME}` ] ; then
    aws lambda delete-function --function-name ${FUNCTION_NAME}
fi

# そのまま実行すると次の処理に進まなくなるので & でバックグラウンド処理して sleep
aws lambda create-function \
    --function-name ${FUNCTION_NAME} \
    --runtime python3.9 \
    --zip-file fileb://lambda_function.zip  \
    --handler "lambda_function.lambda_handler" \
    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${IAM_ROLE_NAME} &

#    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/lambda-url-role

sleep 10

# 関数 URL のエンドポイント作成
#if [ `aws lambda list-function-url-configs --function-name ${FUNCTION_NAME} --query 'FunctionUrlConfigs[].FunctionUrl'` ] ; then
#    aws lambda delete-function-url-config --function-name ${FUNCTION_NAME}
#fi
set +eu
aws lambda delete-function-url-config --function-name ${FUNCTION_NAME}
set -eu

aws lambda create-function-url-config \
    --function-name ${FUNCTION_NAME} \
    --auth-type NONE

#    --cors 'AllowCredentials=false,AllowMethods=GET,AllowOrigins=*'

# Lambda 関数に関数URLにアクセスできるようにするためのリソースポリシーを追加する
aws lambda add-permission \
    --function-name ${FUNCTION_NAME} \
    --function-url-auth-type NONE \
    --statement-id FunctionURLAllowPublicAccess \
    --principal "*" \
    --action lambda:InvokeFunctionUrl  
  
#-----------------------------
# Lambda 関数を呼び出す
#-----------------------------
# 同期呼び出し
aws lambda invoke \
    --function-name ${FUNCTION_NAME} \
    --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
    --cli-binary-format raw-in-base64-out response.json

# 非同期呼び出し
aws lambda invoke \
    --invocation-type Event \
    --function-name ${FUNCTION_NAME} \
    --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
    --cli-binary-format raw-in-base64-out response.json

# 関数 URL を呼び出し
FUNCTION_URL=`aws lambda get-function-url-config --function-name ${FUNCTION_NAME} --query FunctionUrl`
curl ${FUNCTION_URL}
