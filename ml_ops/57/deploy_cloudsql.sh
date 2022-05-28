#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004
REGION=us-central1
SQL_INSTANCE_NAME=mysql-instance-220528
N_CPUS=2
MEMORY_SIZE=7680MB
PASSWORD=1234

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

gcloud sql instances list

#-----------------------------------------------
# SQL インスタンスへ接続する
#-----------------------------------------------
