#!/bin/sh
set -eu
ROOT_DIR=${PWD}
AWS_PROFILE_NAME=Yagami360
CONTAINER_NAME="terraform-aws-container"

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

echo "aws version : `aws --version`"

#-----------------------------
# 認証情報を設定する。
#-----------------------------
# プロファイルを設定
if [ ! -e "${HOME}/.aws/credentials" ] ; then
    aws configure --profile ${AWS_PROFILE_NAME}
    aws configure set region ${AWS_REGION}
fi

# デフォルトユーザーを設定
export AWS_DEFAULT_PROFILE=${AWS_PROFILE_NAME}

# 作成したプロファイルの認証情報を確認
cat ${HOME}/.aws/credentials

#-----------------------------
# terraform コンテナ起動
#-----------------------------
cd terraform/aws
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d

#-----------------------------
# Amazon S3 パケット作成（tfstate保存用）
#-----------------------------
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd s3 && terraform init -upgrade"
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd s3 terraform plan"
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd s3 && terraform apply -auto-approve"
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd s3 && terraform show"

#-----------------------------
# Amazon EKS クラスター & ノードプール作成
#-----------------------------
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd eks && terraform init -upgrade"
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd eks terraform plan"
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd eks && terraform apply -auto-approve -var 'key_name=KEY'"
docker exec -it ${CONTAINER_NAME} /bin/sh -c "cd eks && terraform show"

#-----------------------------
# kubeconfig と ConfigMap の反映
#-----------------------------
cd ${ROOT_DIR}

# 作成した EKS クラスターの kubeconfig を反映する
terraform output kubeconfig > ${HOME}/kube/config
export KUBECONFIG='${HOME}/kube/config'

#
mkdir -p k8s
terraform output eks_configmap > k8s/eks_configmap.yml
kubectl apply -f k8s/eks_configmap.yaml
