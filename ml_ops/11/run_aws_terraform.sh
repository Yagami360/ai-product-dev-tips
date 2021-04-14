#!/bin/sh
set -eu
AWS_PROFILE_NAME=Yagami360
AWS_IAM_USER_NAME=developer
AWS_IAM_GROUP_NAME=developers
AWS_REGION=us-west-2
TERRAFORM_DIR=terraform

# OS 判定
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

#brew update

#=============================
# AWS の事前準備
#=============================
#-----------------------------
# AWS CLI のインストール
#-----------------------------
if [ ${OS} = "Mac" ] ; then
    brew install awscli
elif [ ${OS} = "Linux" ] ; then
    # pip インストール / --user で、pipのスクリプトを ~/.local/bin にインストール
    curl -O https://bootstrap.pypa.io/get-pip.py
    python get-pip.py --user 
    echo export PATH='~/.local/bin:$PATH' >> ~/.bash_profile
    source ~/.bash_profile
    pip --version

    # aws-cliインストール / --user で、pipのスクリプトを ~/.local/bin にインストール
    pip install awscli --upgrade --user
fi

echo "aws cli path : `which aws`"
echo "aws cli version : `aws --version`"

#-----------------------------
# 認証情報を設定する。
#-----------------------------
# プロファイルを設定
#aws configure
aws configure --profile ${AWS_PROFILE_NAME}
aws configure set region ${AWS_REGION}

# デフォルトユーザーを設定
export AWS_DEFAULT_PROFILE=${AWS_PROFILE_NAME}

#-----------------------------
# IAM ユーザーを作成する
#-----------------------------
# IAM ユーザーを作成
#aws iam create-access-key --user-name ${AWS_IAM_USER_NAME}

# アクセスキーを作成
#aws iam create-access-key --user-name ${AWS_IAM_USER_NAME}

# ユーザーをグループに登録
#aws iam add-user-to-group --group-name ${AWS_IAM_GROUP_NAME} --user-name ${AWS_IAM_USER_NAME}

#-----------------------------
# 設定した認証情報と IAM ユーザーを確認する
#-----------------------------
# 現在のプロファイルを確認
aws configure list

# IAM ユーザーを確認
aws iam list-users

# IAM グループを確認
aws iam list-groups

#=============================
# Terraform を用いた AWS インスタンスの作成
#=============================
# Terraform のインストール
if [ ${OS} = "Mac" ] ; then
    brew install terraform
fi

cd ${TERRAFORM_DIR}
#terraform destroy

# terraform の初期化
if [ ! -e ".terraform" ] ; then
  terraform init
fi

# 定義内容のチェック
terraform plan

# 定義を適用してインスタンスを作成する
terraform apply

# terraform が作成したオブジェクトの内容を確認
terraform show

# EC インスタンスコンソールを確認
#aws ec2 describe-instances
if [ ${OS} = "Mac" ] ; then
    open https://${AWS_REGION}.console.aws.amazon.com/ec2/v2/home?region=${AWS_REGION}#Instances:
    open https://${AWS_REGION}.console.aws.amazon.com/vpc/home?region=${AWS_REGION}#vpcs:
fi

# IP アドレス可能
terraform show | grep public_ip

# ssh 接続
#ssh ubuntu@${IP_ADRESS}
