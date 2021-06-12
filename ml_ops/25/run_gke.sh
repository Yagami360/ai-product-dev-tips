#!/bin/sh
set -eu

PROJECT_ID=my-project2-303004

REGION=asia-northeast1
#REGION=us-central1
ZONE=asia-northeast1-a
#ZONE=us-central1-c

CLUSTER_NAME=fast-api-cluster
CPU_TYPE=n1-standard-4
POD_NAME=fast-api-pod
SERVICE_NAME=fast-api-server
MIN_NODES=1
MAX_NODES=4

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}
gcloud config set compute/zone ${ZONE}
gcloud config list

# docker image を GCP の Container Registry にアップロード
gcloud builds submit --config cloudbuild.yml

# クラスタを作成
if [ "$(gcloud container clusters list | grep "${CLUSTER_NAME}")" ] ;then
    gcloud container clusters delete ${CLUSTER_NAME} --region ${ZONE}
fi

gcloud container clusters create ${CLUSTER_NAME} \
    --region ${ZONE} \
    --machine-type ${CPU_TYPE} \
    --min-nodes ${MIN_NODES} --max-nodes ${MAX_NODES} \
    --enable-autoscaling

# API の Pod を作成する
kubectl apply -f api/k8s/deployment.yml

# vegeta attack の Pod を作成する
kubectl apply -f vegeta/k8s/deployment.yml

# API の Service を公開する
kubectl apply -f api/k8s/service.yml

sleep 60
kubectl get pods
kubectl get service ${SERVICE_NAME}

# 作成した Pod のコンテナログを確認
#POD_NAME=`kubectl get pods | awk '{print $1}' | sed -n 2p`
#kubectl logs ${POD_NAME}
#kubectl top pod

# 作成した Pod のコンテナにアクセス
#kubectl exec -it ${POD_NAME} /bin/bash
