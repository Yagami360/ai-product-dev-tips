#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"
ZONE="us-west-2a"

ECR_REPOSITORY_NAME=predict-server-image
COMPUTE_ENV_NAME="aws-batch-compute-environment-2"
JOB_QUEUE_NAME="aws-batch-job-queue"
JOB_DEFINITION_NAME="aws-batch-job-definition"

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
#export AWS_ACCOUNTID=${AWS_ACCOUNT_ID}
#cat ~/.aws/credentials

# AWS CLI のプロファイル
#export AWS_PROFILE=${AWS_PROFILE}
#export AWS_DEFAULT_REGION=${REGION}
#cat ~/.aws/config

#=============================
# AWS Bacth リソース削除
#=============================
# ECR リポジトリを作成する
#if [ "$( aws ecr batch-get-repository-scanning-configuration --repository-names ${ECR_REPOSITORY_NAME} --query scanningConfigurations[*].repositoryName | grep "${ECR_REPOSITORY_NAME}")" ] ; then
#    if [ "$( aws ecr list-images --repository-name ${ECR_REPOSITORY_NAME} --query imageIds[*].imageTag | grep "latest")" ] ; then
#        aws ecr batch-delete-image --repository-name ${ECR_REPOSITORY_NAME} --image-ids imageTag=latest
#    fi
#    aws ecr delete-repository --repository-name ${ECR_REPOSITORY_NAME}
#fi

# ジョブ定義
if [ $( aws batch describe-job-definitions --job-definition-name ${JOB_DEFINITION_NAME} --query jobDefinitions[*].jobDefinitionName | grep ${JOB_DEFINITION_NAME} ) ] ; then
  aws batch deregister-job-definition --job-definition ${JOB_DEFINITION_NAME}
  #for arn in $( aws batch describe-job-definitions --job-definition-name ${JOB_DEFINITION_NAME} --query jobDefinitions[*].jobDefinitionArn --output text )
  #do
  #  aws batch deregister-job-definition --job-definition $arn
  #done
  sleep 5
fi

# ジョブキュー
if [ $( aws batch describe-job-queues --job-queue ${JOB_QUEUE_NAME} --query jobQueues[*].jobQueueName | grep ${JOB_QUEUE_NAME} ) ] ; then
  aws batch update-job-queue --job-queue ${JOB_QUEUE_NAME} --state DISABLED
  sleep 5
  aws batch delete-job-queue --job-queue ${JOB_QUEUE_NAME}
  sleep 10
fi

# コンピューティング環境
if [ $( aws batch describe-compute-environments --compute-environments ${COMPUTE_ENV_NAME} --query computeEnvironments[*].computeEnvironmentName | grep ${COMPUTE_ENV_NAME} ) ] ; then
  aws batch update-compute-environment --compute-environment ${COMPUTE_ENV_NAME} --state "DISABLED"
  sleep 5
  aws batch delete-compute-environment --compute-environment ${COMPUTE_ENV_NAME}
fi
