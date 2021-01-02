#!/bin/sh
set -eu

PROJECT_ID=myproject-292103
REGION=asia-northeast1-a
IMAGE_NAME=sample-image
CLUSTER_NAME=sample-cluster
SERVICE_NAME=sample-server
NUM_NODES=2
POD_NAME=sample-pod
PORT=5000
TARGET_PORT=5000

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${REGION}
gcloud config list

# docker image の作成
#docker-compose -f docker-compose.yml stop
#docker-compose -f docker-compose.yml up -d

# docker image を GCP の Container Registry にアップロード
#gcloud builds submit --tag gcr.io/${PROJECT_ID}/${IMAGE_NAME}
gcloud builds submit --config api/cloudbuild.yml

# １つのノードのクラスタを作成（デフォルトでは３ノード）
gcloud container clusters create ${CLUSTER_NAME} --num-nodes=${NUM_NODES}

# クラスタの認証情報を取得する
#gcloud container clusters get-credentials ${CLUSTER_NAME}

# Deployment を作成する
#kubectl create deployment ${CLUSTER_NAME} --image=gcr.io/${PROJECT_ID}/${IMAGE_NAME}
kubectl apply -f k8s/deployment.yml
kubectl get pods
kubectl get deployments

# Deployment を公開する
#kubectl expose deployment ${SERVICE_NAME} --type LoadBalancer --port ${PORT} --target-port ${TARGET_PORT}
kubectl apply -f k8s/service.yml
kubectl get service ${SERVICE_NAME}

# 公開サイトにアクセスして動作確認する

# 作成した POd のコンテナにアクセス