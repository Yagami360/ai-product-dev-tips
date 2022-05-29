#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004
REGION=us-central1
CLOUD_COMPOSER_ENV_NAME="cloud-composer-v1-env"

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
# Cloud Composer API の有効化
#-----------------------------------------------
gcloud services enable composer.googleapis.com

#-----------------------------------------------
# Cloud Composer 環境を作成する
#-----------------------------------------------
if [ "$(gcloud composer environments list --locations ${REGION} | grep ${CLOUD_COMPOSER_ENV_NAME})" ] ;then
    gcloud composer environments delete ${CLOUD_COMPOSER_ENV_NAME} --location ${REGION}
fi

if [ ! "$(gcloud composer environments list --locations ${REGION} | grep ${CLOUD_COMPOSER_ENV_NAME})" ] ;then
    gcloud composer environments create ${CLOUD_COMPOSER_ENV_NAME} \
        --location ${REGION} \
        --image-version composer-1.18.5-airflow-1.10.15
fi

#-----------------------------------------------
# 作成した DAG スクリプトを GCS にアップロードする
#-----------------------------------------------
gcloud composer environments storage dags import \
    --environment ${CLOUD_COMPOSER_ENV_NAME}  --location ${REGION} \
    --source dag.py

#-----------------------------------------------
# DAG を実行する
#-----------------------------------------------
sleep 10
gcloud composer environments run ${CLOUD_COMPOSER_ENV_NAME} \
    --location ${REGION} \
    dags trigger -- "cloud_composer_v1_dag"
