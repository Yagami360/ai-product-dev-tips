#!/bin/sh
set -eu
IAM_ROLE_NAME_1="AWSBatchServiceRole"
IAM_POLICY_FILE_PATH_1="aws-batch-service-iam-policy.json"

IAM_ROLE_NAME_2="ecsInstanceRole"
IAM_POLICY_FILE_PATH_2="aws-batch-ec2-iam-policy.json"

# AWSBatchServiceRole
if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME_1}` ] ; then
    # IAM ロールを作成する
    aws iam create-role \
        --role-name ${IAM_ROLE_NAME_1} \
        --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH_1}"

    sleep 10

    # 作成した IAM ロールに IAM ポリシーを付与する
    aws iam attach-role-policy \
        --role-name ${IAM_ROLE_NAME_1} \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole
fi

# ecsInstanceRole
if [ ! `aws iam list-roles --query 'Roles[].RoleName' | grep ${IAM_ROLE_NAME_2}` ] ; then
    # IAM ロールを作成する
    aws iam create-role \
        --role-name ${IAM_ROLE_NAME_2} \
        --assume-role-policy-document "file://${IAM_POLICY_FILE_PATH_2}"

    sleep 10

    # 作成した IAM ロールに IAM ポリシーを付与する
    aws iam attach-role-policy \
        --role-name ${IAM_ROLE_NAME_2} \
        --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role
fi
