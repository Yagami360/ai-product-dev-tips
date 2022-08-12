#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
AWS_REGION=us-west-2

LAMBDA_IAM_ROLE_NAME="lambda-iam-role"
LAMBDA_IAM_POLICY_FILE_PATH="lambda-iam-policy.json"
FUNCTION_NAME_1="lambda-function-1"
FUNCTION_NAME_2="lambda-function-2"

STEPFUNTIONS_IAM_ROLE_NAME="stepfuntions-iam-role"
STEPFUNTIONS_IAM_POLICY_FILE_PATH="stepfuntions-iam-policy.json"
STATEMACHINE_NAME="hellow-world-lambda-statemachine-cli"
STATEMACHINE_DEFINITION_FILE_PATH="statemachine_definition.json"
STATEMACHINE_INPUT_JSON_PATH="statemachine_input.json"

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

# AWS CLI を設定する環境変数
export AWS_ACCOUNTID=${AWS_ACCOUNT_ID}
export AWS_PROFILE=${AWS_PROFILE}
export AWS_DEFAULT_REGION=${AWS_REGION}

cat ~/.aws/config
cat ~/.aws/credentials

#=============================
# リソース削除
#=============================
sh delete_aws_stepfuntions.sh

#=============================
# Lambda 関数の作成
#=============================
mkdir -p logs

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
rm -rf lambda_function_1.zip
rm -rf lambda_function_2.zip

zip -r lambda_function_1.zip lambda_function_1.py
zip -r lambda_function_2.zip lambda_function_2.py

#-----------------------------
# Lambda 関数を作成する
#-----------------------------
# aws lambda create-function を実行するとコンソール出力画面で待機状態になるので、`> ${FUNCTION_NAME}.json` で json ファイルに外部出力する
aws lambda create-function \
    --function-name ${FUNCTION_NAME_1} \
    --runtime python3.9 \
    --zip-file fileb://lambda_function_1.zip  \
    --handler "lambda_function_1.lambda_handler" \
    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${LAMBDA_IAM_ROLE_NAME} > logs/${FUNCTION_NAME_1}.json

aws lambda create-function \
    --function-name ${FUNCTION_NAME_2} \
    --runtime python3.9 \
    --zip-file fileb://lambda_function_2.zip  \
    --handler "lambda_function_2.lambda_handler" \
    --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${LAMBDA_IAM_ROLE_NAME} > logs/${FUNCTION_NAME_2}.json

rm -rf lambda_function_1.zip
rm -rf lambda_function_2.zip

sleep 10

# 関数 URL のエンドポイント作成
aws lambda create-function-url-config \
    --function-name ${FUNCTION_NAME_1} \
    --auth-type NONE

aws lambda create-function-url-config \
    --function-name ${FUNCTION_NAME_2} \
    --auth-type NONE

#    --cors 'AllowCredentials=false,AllowMethods=GET,AllowOrigins=*'

# Lambda 関数に関数URLにアクセスできるようにするためのリソースポリシーを追加する
aws lambda add-permission \
    --function-name ${FUNCTION_NAME_1} \
    --function-url-auth-type NONE \
    --statement-id FunctionURLAllowPublicAccess \
    --principal "*" \
    --action lambda:InvokeFunctionUrl  
  
aws lambda add-permission \
    --function-name ${FUNCTION_NAME_2} \
    --function-url-auth-type NONE \
    --statement-id FunctionURLAllowPublicAccess \
    --principal "*" \
    --action lambda:InvokeFunctionUrl

#-----------------------------
# Lambda 関数を呼び出す
#-----------------------------
# 同期呼び出し
#aws lambda invoke \
#    --function-name ${FUNCTION_NAME_1} \
#    --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
#    --cli-binary-format raw-in-base64-out logs/response_1.json

#aws lambda invoke \
#    --function-name ${FUNCTION_NAME_2} \
#    --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
#    --cli-binary-format raw-in-base64-out logs/response_2.json

# 非同期呼び出し
#aws lambda invoke \
#    --invocation-type Event \
#    --function-name ${FUNCTION_NAME_1} \
#    --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
#    --cli-binary-format raw-in-base64-out logs/response_1_async.json

#aws lambda invoke \
#    --invocation-type Event \
#    --function-name ${FUNCTION_NAME_2} \
#    --payload '{"key1":" value1", "key2":"value2", "key3":"value3"}' \
#    --cli-binary-format raw-in-base64-out logs/response_2_async.json

# 関数 URL を呼び出し
FUNCTION_URL_1=`aws lambda get-function-url-config --function-name ${FUNCTION_NAME_1} --query FunctionUrl --output text`
echo "FUNCTION_URL_1 : ${FUNCTION_URL_1}"
curl ${FUNCTION_URL_1}

FUNCTION_URL_2=`aws lambda get-function-url-config --function-name ${FUNCTION_NAME_2} --query FunctionUrl --output text`
echo "FUNCTION_URL_2 : ${FUNCTION_URL_2}"
curl ${FUNCTION_URL_2}

#=============================
# Step Funtions の作成
#=============================
# AWS Step Functions 用の IAM role を作成する
if [ ! $( aws iam list-roles --query 'Roles[*].RoleName' | grep ${STEPFUNTIONS_IAM_ROLE_NAME} ) ] ; then
    # Lambda 関数実行のための IAM ロールを作成する
    aws iam create-role \
        --role-name ${STEPFUNTIONS_IAM_ROLE_NAME} \
        --assume-role-policy-document "file://${STEPFUNTIONS_IAM_POLICY_FILE_PATH}"

    # 作成した IAM ロールに、lambda 関数にアクセスできるようにするための IAM ポリシーを付与する
    aws iam attach-role-policy \
        --role-name ${STEPFUNTIONS_IAM_ROLE_NAME} \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

    sleep 10
fi

# ステートマシンを作成する
aws stepfunctions create-state-machine \
    --name ${STATEMACHINE_NAME} \
    --definition file://${STATEMACHINE_DEFINITION_FILE_PATH} \
    --role-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/${STEPFUNTIONS_IAM_ROLE_NAME}

# ステートマシンを実行する
EXECUTION_NAME="exxcution_1"
aws stepfunctions start-execution \
    --name ${EXECUTION_NAME} \
    --state-machine-arn arn:aws:states:${AWS_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${STATEMACHINE_NAME} \
    --input file://${STATEMACHINE_INPUT_JSON_PATH}

# ステートマシンの実行結果を確認する
aws stepfunctions describe-execution \
    --execution-arn arn:aws:states:${AWS_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${STATEMACHINE_NAME}:${EXECUTION_NAME}
