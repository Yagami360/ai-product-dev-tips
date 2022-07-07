#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"
ZONE="us-west-2a"

IMAGE_NAME=job-image
ECR_REPOSITORY_NAME=${IMAGE_NAME}
#ENABLE_BUILD=0
ENABLE_BUILD=1

SUBNET_ID_1="subnet-fd3dd885"
SUBNET_ID_2="subnet-d2292f99"
SUBNET_ID_3="subnet-b1f601ec"
SUBNET_ID_4="subnet-6fa0cf44"
SECURITY_GROUP_ID="sg-9c562fd9"

COMPUTE_ENV_NAME="aws-batch-compute-environment-2"
JOB_QUEUE_NAME="aws-batch-job-queue"
JOB_DEFINITION_NAME="aws-batch-job-definition"
JOB_NAME="aws-batch-job"

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
# IAM ロールの作成
#=============================
#sh make_iam.sh

#=============================
# AWS Bacth リソース削除
#=============================
sh delete_aws_batch.sh

#=============================
# Amazon ECR に Docker image を push する
#=============================
if [ ! ${ENABLE_BUILD} = 0 ] ; then
    # Docker image を作成する
    cd job
    docker build ./ -t ${IMAGE_NAME}
    cd ..

    # ECR リポジトリを作成する
    if [ "$( aws ecr batch-get-repository-scanning-configuration --repository-names ${ECR_REPOSITORY_NAME} --query scanningConfigurations[*].repositoryName | grep "${ECR_REPOSITORY_NAME}")" ] ; then
        if [ "$( aws ecr list-images --repository-name ${ECR_REPOSITORY_NAME} --query imageIds[*].imageTag | grep "latest")" ] ; then
            aws ecr batch-delete-image --repository-name ${ECR_REPOSITORY_NAME} --image-ids imageTag=latest
        fi
        aws ecr delete-repository --repository-name ${ECR_REPOSITORY_NAME}
    fi
    aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --image-scanning-configuration scanOnPush=true

    # ECR にログインする
    aws ecr get-login-password --profile ${AWS_PROFILE} --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

    # ローカルの docker image に ECR リポジトリ名での tag を付ける
    docker tag ${IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest

    # ECR に Docker image を push する
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest
fi

#=============================
# IAM の作成
#=============================
sh make_iam.sh

#=============================
# AWS Batch リソース作成
#=============================
#-----------------------------
# コンピューティング環境を作成
#-----------------------------
# コンピューティング環境（起動する EC2 インスタンス環境）を定義した json ファイルを作成する。
cat << EOF > ${COMPUTE_ENV_NAME}.spec.json
{
    "computeEnvironmentName": "${COMPUTE_ENV_NAME}",
    "type": "MANAGED",
    "state": "ENABLED",
    "computeResources": {
        "type": "EC2",
        "minvCpus": 0,
        "maxvCpus": 4,
        "desiredvCpus": 0,
        "instanceTypes": ["optimal"],
        "subnets": ["${SUBNET_ID_1}", "${SUBNET_ID_2}", "${SUBNET_ID_3}", "${SUBNET_ID_4}"],
        "securityGroupIds": ["${SECURITY_GROUP_ID}"],
        "instanceRole": "arn:aws:iam::${AWS_ACCOUNT_ID}:instance-profile/ecsInstanceRole"
    },
    "serviceRole": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/AWSBatchServiceRole"
}
EOF

# コンピューティング環境（起動する EC2 インスタンス環境）を作成する
aws batch create-compute-environment --cli-input-json file://${COMPUTE_ENV_NAME}.spec.json

#-----------------------------
# ジョブキューの作成
#-----------------------------
# ジョブキューを作成
aws batch create-job-queue \
  --job-queue-name ${JOB_QUEUE_NAME} \
  --priority 1 \
  --compute-environment-order order=1,computeEnvironment="arn:aws:batch:${REGION}:${AWS_ACCOUNT_ID}:compute-environment/${COMPUTE_ENV_NAME}" > ${JOB_QUEUE_NAME}.log

# ジョブキューの ARN を取得
JOB_QUEUE_ARN=$(jq -r '.jobQueueArn' ${JOB_QUEUE_NAME}.log)
echo "JOB_QUEUE_ARN : ${JOB_QUEUE_ARN}"

#-----------------------------
# ジョブ定義の作成
#-----------------------------
# ジョブ定義を記述した json ファイルを作成する
cat << EOF > ${JOB_DEFINITION_NAME}.spec.json
{
  "image": "${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:latest",
  "command": ["python", "job.py", "--ok_or_ng", "Ref::ok_or_ng"],
  "vcpus": 1,
  "memory": 500
}
EOF

# ジョブ定義を作成する
aws batch register-job-definition \
  --job-definition-name ${JOB_DEFINITION_NAME} \
  --type container \
  --container-properties file://${JOB_DEFINITION_NAME}.spec.json \
  --parameters ok_or_ng="ok" > ${JOB_DEFINITION_NAME}.log

# ジョブ定義の ARN を取得
JOB_DEFINITION_ARN=$(jq -r '.jobDefinitionArn' ${JOB_DEFINITION_NAME}.log)
echo "JOB_DEFINITION_ARN : ${JOB_DEFINITION_ARN}"

#-----------------------------
# ジョブの送信
#-----------------------------
aws batch submit-job \
  --job-name "${JOB_NAME}" \
  --job-queue "${JOB_QUEUE_ARN}" \
  --job-definition "${JOB_DEFINITION_ARN}" \
  --parameters ok_or_ng="ok" > ${JOB_NAME}.log
