#!/bin/sh
set -eu
AWS_PROFILE_NAME=Yagami360
CONTAINER_NAME="terraform-container"

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
# terraform
#-----------------------------
# terraform コンテナ起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d

# terraform を初期化する。
docker exec -it ${CONTAINER_NAME} /bin/sh -c "terraform init"

# 作成したテンプレートファイルの定義内容を確認する
docker exec -it ${CONTAINER_NAME} /bin/sh -c "terraform plan"

# 定義を適用してインスタンスを作成する
docker exec -it ${CONTAINER_NAME} /bin/sh -c "terraform apply"

# terraform が作成したオブジェクトの内容を確認
docker exec -it ${CONTAINER_NAME} /bin/sh -c "terraform show"
