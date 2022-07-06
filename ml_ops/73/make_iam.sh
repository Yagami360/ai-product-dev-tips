#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
#IAM_ROLE_NAME="aws-batch-role"
IAM_ROLE_NAME="AWSBatchServiceRole"
IAM_POLICY_FILE_PATH="aws-batch-iam-policy.json"

if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME}` ] ; then
    # Datadog　から各種 EC2 インスタンスにアクセスするための IAM ロールを作成する
    aws iam create-role \
        --role-name ${IAM_ROLE_NAME} \
        --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH}"

    sleep 10

    # 作成した IAM ロールに IAM ポリシーを付与する
    aws iam attach-role-policy \
        --role-name ${IAM_ROLE_NAME} \
        --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:role/service-role/AWSBatchServiceRole
fi
