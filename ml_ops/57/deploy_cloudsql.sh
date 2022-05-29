#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004
REGION=us-central1
SQL_INSTANCE_NAME="mysql-instance-$(date "+%Y%m%d")"
N_CPUS=2
MEMORY_SIZE=7680MB
PASSWORD=1234

#-----------------------------
# OS判定
#-----------------------------
if [ "$(uname)" = 'Darwin' ]; then
  OS='Mac'
  echo "Your platform is Mac."  
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

#-----------------------------------------------
# GCP 環境のデフォルト値の設定
#-----------------------------------------------
gcloud --version
gcloud config set project ${PROJECT_ID}
gcloud config list

#-----------------------------------------------
# Google Cloud SQL API の有効化
#-----------------------------------------------
#gcloud services list --available
gcloud services enable sqladmin.googleapis.com

#-----------------------------------------------
# MySQL 用の SQL インスタンス（VMインスタンス）を作成する
#-----------------------------------------------
# SQL インスタンスを作成する
gcloud sql instances create ${SQL_INSTANCE_NAME} \
    --database-version=MYSQL_8_0 \
    --cpu=${N_CPUS} \
    --memory=${MEMORY_SIZE} \
    --region=${REGION}

# 作成した SQL インスタンスの root ユーザーのパスワードを設定する
gcloud sql users set-password root \
    --host=% \
    --instance ${SQL_INSTANCE_NAME} \
    --password ${PASSWORD}

#gcloud sql instances list

#-----------------------------------------------
# Cloud SQL Auth Proxy を起動し、SQL インスタンスの接続可能状態にする
#-----------------------------------------------
#gcloud sql connect ${SQL_INSTANCE_NAME} --user=root

# Cloud SQL Auth Proxy をダウンロードしてインストールする
if [ ${OS} = "Mac" ] ; then
    if [ "$(uname -m)" = 'x86_64' ]; then
        # Mac (64bit) の場合
        curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64
        chmod +x cloud_sql_proxy
    elif [ "$(uname -m)" = 'x86_64' ]; then
        # Mac (M1) の場合
        curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.arm64
        chmod +x cloud_sql_proxy
    else
        curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64
        chmod +x cloud_sql_proxy
    fi
elif [ ${OS} = "Linux" ] ; then
    wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
    chmod +x cloud_sql_proxy
else
    wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
    chmod +x cloud_sql_proxy
fi

# Cloud SQL Auth Proxy を起動する
./cloud_sql_proxy -instances=${PROJECT_ID}:${REGION}:${SQL_INSTANCE_NAME}=tcp:3306
