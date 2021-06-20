#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004
SERVICE_ACCOUNT_NAME=logging

REGION=asia-northeast1
ZONE=asia-northeast1-a
CPU_TYPE=n1-standard-4

CLUSTER_NAME=fastapi-cluster
SERVICE_NAME=fastapi-server
NUM_NODES=1
MIN_NODES=1
MAX_NODES=1

ENABLE_BUILD=0
#ENABLE_BUILD=1

HOST=0.0.0.0
PORT=5000

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}
gcloud config set compute/zone ${ZONE}
gcloud config list

# docker image を Cloud Build 上でビルドし、GCP Container Registry にアップロード
cd api/
if [ ! ${ENABLE_BUILD} = 0 ] ; then
    gcloud builds submit --config cloudbuild.yml
fi
cd ..

# クラスタを作成
if [ "$(gcloud container clusters list | grep "${CLUSTER_NAME}")" ] ;then
    gcloud container clusters delete ${CLUSTER_NAME} --region ${ZONE}
fi

gcloud container clusters create ${CLUSTER_NAME} \
    --region ${ZONE} \
    --machine-type ${CPU_TYPE} \
    --num-nodes ${NUM_NODES} \
    --min-nodes ${MIN_NODES} --max-nodes ${MAX_NODES} \
    --enable-autoscaling

#    --scopes=gke-default,logging-write

# Config Map を作成する
kubectl apply -f k8s/configmap.yml

# API の Pod を作成する
kubectl apply -f k8s/deployment.yml
kubectl get pods

# API の Service を公開する
kubectl apply -f k8s/service.yml

# 作成した Pod のコンテナログを確認
#kubectl logs `kubectl get pods | grep "fast-api-pod" | awk '{print $1}'` fast-api-container
#kubectl logs `kubectl get pods | grep "fast-api-pod" | awk '{print $1}'` fluentd-container

# 作成した Pod のコンテナにアクセス
#kubectl exec -it `kubectl get pods | grep "fast-api-pod" | awk '{print $1}'` /bin/bash
