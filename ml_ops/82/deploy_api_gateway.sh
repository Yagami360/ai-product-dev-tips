#!/bin/sh
set -eu
#AWS_ACCOUNT_ID=735015535886
AWS_ACCOUNT_ID=241325567245
AWS_PROFILE=Yagami360
REGION="us-west-2"

LAMBDA_IAM_ROLE_NAME="lambda-iam-role"
LAMBDA_IAM_POLICY_FILE_PATH="lambda-iam-policy.json"
LAMBDA_FUNCTION_NAME="lambda-function"

REST_API_NAME="rest-api"

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
sh delete_api_gateway.sh

#=============================
# リソース作成
#=============================
mkdir -p log

#-----------------------------
# Lambda 関数実行のための IAM を作成する
#-----------------------------
if [ ! $( aws iam list-roles --query 'Roles[*].RoleName' | grep ${LAMBDA_IAM_ROLE_NAME} ) ] ; then
    # Lambda 関数実行のための IAM ロールを作成する
    aws iam create-role \
        --role-name ${LAMBDA_IAM_ROLE_NAME} \
        --assume-role-policy-document "file://${LAMBDA_IAM_POLICY_FILE_PATH}"

    # 作成した IAM ロールに、Lambda サービスにアクセスできるようにするための IAM ポリシーを付与する
    aws iam attach-role-policy \
        --role-name ${LAMBDA_IAM_ROLE_NAME} \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    # IAM role 作成直後に aws lambda create-function コマンドで lambda 関数を作成するとエラー人あるので sleep
    sleep 10
fi

#-----------------------------
# API コードを zip ファイルにする
#-----------------------------
zip -r lambda_function.zip lambda_function.py

#-----------------------------
# Lambda 関数を作成する
#-----------------------------
aws lambda create-function \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --runtime python3.9 \
    --zip-file fileb://lambda_function.zip  \
    --handler "lambda_function.lambda_handler" \
    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${LAMBDA_IAM_ROLE_NAME} > log/${LAMBDA_FUNCTION_NAME}.json

sleep 10

# 関数 URL のエンドポイント作成
aws lambda create-function-url-config \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --auth-type NONE

#    --cors 'AllowCredentials=false,AllowMethods=GET,AllowOrigins=*'

# Lambda 関数に関数URLにアクセスできるようにするためのリソースポリシーを追加する
aws lambda add-permission \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --function-url-auth-type NONE \
    --statement-id FunctionURLAllowPublicAccess \
    --principal "*" \
    --action lambda:InvokeFunctionUrl  
  
#-----------------------------
# Lambda 関数を呼び出す
#-----------------------------
# 同期呼び出し
aws lambda invoke \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
    --cli-binary-format raw-in-base64-out response.json

# 非同期呼び出し
aws lambda invoke \
    --invocation-type Event \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
    --cli-binary-format raw-in-base64-out response.json

# 関数 URL を呼び出し
LAMBDA_FUNCTION_URL=`aws lambda get-function-url-config --function-name ${LAMBDA_FUNCTION_NAME} --query FunctionUrl --output text`
echo "LAMBDA_FUNCTION_URL : ${LAMBDA_FUNCTION_URL}"
curl ${LAMBDA_FUNCTION_URL}

#-----------------------------
# API Gateway を使用して REST API を作成する
#-----------------------------
# REST API 作成 & REST_API_ID 取得
REST_API_ID=$( aws apigateway create-rest-api --name ${REST_API_NAME} | jq -r '.id' )
echo "REST_API_ID : ${REST_API_ID}"

#-----------------------------
# REST API にリソース（エンドポイント）を追加する
#-----------------------------
# ルートエンドポイント "http:${HOST}:${PORT}/ のリソース ID 取得
REST_API_ROOT_ID=$( aws apigateway get-resources --rest-api-id ${REST_API_ID} --query items[*].id --output text )
echo "REST_API_ROOT_ID : ${REST_API_ROOT_ID}"

# ルートエンドポイント以下に別のエンドポイントを追加
REST_API_ENDPOINT_ID=$( aws apigateway create-resource --rest-api-id ${REST_API_ID} --parent-id ${REST_API_ROOT_ID} --path-part "hello" | jq -r '.id' )
echo "REST_API_ENDPOINT_ID : ${REST_API_ENDPOINT_ID}"    

# 全エンドポイント確認
aws apigateway get-resources --rest-api-id ${REST_API_ID}

#-----------------------------
# 作成した REST API に GET リクエストを追加する
#-----------------------------
# メソッドリクエスト（クライアントから API Gateway <REST API> へのリクエスト）を追加する
aws apigateway put-method \
    --rest-api-id ${REST_API_ID} \
    --resource-id ${REST_API_ENDPOINT_ID} \
    --http-method GET \
    --authorization-type NONE \
    --no-api-key-required \
    --request-parameters {}
    
# 統合リクエスト（API Gateway <REST API> から Lambda へのリクエスト）を追加する
aws apigateway put-integration \
    --rest-api-id ${REST_API_ID} \
    --resource-id ${REST_API_ENDPOINT_ID} \
    --http-method GET \
    --integration-http-method POST \
    --type AWS \
    --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${AWS_ACCOUNT_ID}:function:${LAMBDA_FUNCTION_NAME}/invocations"

# 統合レスポンス（Lambda から API Gateway へのレスポンス）を追加する
aws apigateway put-method-response \
    --rest-api-id ${REST_API_ID} \
    --resource-id ${REST_API_ENDPOINT_ID} \
    --http-method POST \
    --status-code 200 \
    --response-models '{"application/json": "Empty"}'

# メソッドレスポンス（API Gateway からクライアントへのレスポンス）を追加する
aws apigateway put-integration-response \
    --rest-api-id ${REST_API_ID} \
    --resource-id ${REST_API_ENDPOINT_ID} \
    --http-method POST \
    --status-code 200 \
    --response-templates '{"application/json": ""}'

