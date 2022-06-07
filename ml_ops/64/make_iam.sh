#!/bin/sh
set -eu
IAM_ROLE_NAME="datadog-ec2iam-role"
IAM_POLICY_FILE_PATH="datadog-ec2-iam-policy.json"
IAM_USER_NAME=datadog
IAM_GROUP_NAME=developers

if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME}` ] ; then
    # Datadog　から各種 EC2 インスタンスにアクセスするための IAM ロールを作成する
    aws iam create-role \
        --role-name ${IAM_ROLE_NAME} \
        --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH}"

    sleep 10

    # 作成した IAM ロールに、Datadog　から各種 EC2 インスタンスにアクセスするための IAM ポリシーを付与する
    aws iam attach-role-policy \
        --role-name ${IAM_ROLE_NAME} \
        --policy-arn arn:aws:ec2:region:account-id:instance/instance-id
fi

# IAM ユーザーを作成
#aws iam create-access-key --user-name ${IAM_USER_NAME}
#aws iam list-users

# アクセスキーを作成
#aws iam create-access-key --user-name ${IAM_USER_NAME}

# ユーザーをグループに登録
#aws iam add-user-to-group --group-name ${IAM_GROUP_NAME} --user-name ${IAM_USER_NAME}
#aws iam list-groups

# 作成した IAM ユーザーに IAM ポリシーを付与する
