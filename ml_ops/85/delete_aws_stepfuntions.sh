#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_REGION=us-west-2

LAMBDA_IAM_ROLE_NAME="lambda-iam-role"
FUNCTION_NAME_1="lambda-function-1"
FUNCTION_NAME_2="lambda-function-2"

STEPFUNTIONS_IAM_ROLE_NAME="stepfuntions-iam-role"
STATEMACHINE_NAME="hellow-world-lambda-statemachine-cli"

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
#echo "aws version : `aws --version`"

#-----------------------------
# リソース削除
#-----------------------------
# Step Funtions の IAM role
if [ $( aws iam list-roles --query 'Roles[*].RoleName' | grep ${STEPFUNTIONS_IAM_ROLE_NAME} ) ] ; then
    aws iam detach-role-policy --role-name ${STEPFUNTIONS_IAM_ROLE_NAME} --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    aws iam delete-role --role-name ${STEPFUNTIONS_IAM_ROLE_NAME}
fi

# Step Funtions のステートマシン
if [ $( aws stepfunctions list-state-machines --query 'stateMachines[*].name' | grep ${STATEMACHINE_NAME} ) ] ; then
    aws stepfunctions delete-state-machine \
        --state-machine-arn "arn:aws:states:${AWS_REGION}:${AWS_ACCOUNT_ID}:stateMachine:${STATEMACHINE_NAME}"
fi

# Lambda 関数の IAM role
if [ $( aws iam list-roles --query 'Roles[*].RoleName' | grep ${LAMBDA_IAM_ROLE_NAME} ) ] ; then
    aws iam detach-role-policy --role-name ${LAMBDA_IAM_ROLE_NAME} --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    aws iam delete-role --role-name ${LAMBDA_IAM_ROLE_NAME}
fi

# Lambda 関数の関数 URL のエンドポイント
if [ $( aws lambda list-functions --query 'Functions[*].FunctionName' | grep ${FUNCTION_NAME_1} ) ] ; then
    if [ $( aws lambda list-function-url-configs --function-name ${FUNCTION_NAME_1} --query 'FunctionUrlConfigs[*].FunctionUrl' --output text ) ] ; then
        aws lambda delete-function-url-config --function-name ${FUNCTION_NAME_1}
    fi
fi

if [ $( aws lambda list-functions --query 'Functions[*].FunctionName' | grep ${FUNCTION_NAME_2} ) ] ; then
    if [ $( aws lambda list-function-url-configs --function-name ${FUNCTION_NAME_2} --query 'FunctionUrlConfigs[*].FunctionUrl' --output text ) ] ; then
        aws lambda delete-function-url-config --function-name ${FUNCTION_NAME_2}
    fi
fi

# Lambda 関数
if [ $( aws lambda list-functions --query 'Functions[*].FunctionName' | grep ${FUNCTION_NAME_1} ) ] ; then
    aws lambda delete-function --function-name ${FUNCTION_NAME_1}
fi

if [ $( aws lambda list-functions --query 'Functions[*].FunctionName' | grep ${FUNCTION_NAME_2} ) ] ; then
    aws lambda delete-function --function-name ${FUNCTION_NAME_2}
fi