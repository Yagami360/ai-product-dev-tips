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

HOST=0.0.0.0
PORT=5000

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}
gcloud config set compute/zone ${ZONE}
gcloud config list

<<COMMENTOUT
# Cloud logging でロギングを行うためのサービスアカウントを作成する
if [ ! "$(gcloud iam service-accounts list | grep ${SERVICE_ACCOUNT_NAME})" ] ;then
    gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME}
fi

# サービスアカウントにロギング権限を付与する
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/logging.logWriter"
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/monitoring.metricWriter"

# サービスアカウントの秘密鍵 (json) を生成する
if [ ! -e "key/key.json" ] ; then
    mkdir -p key
    gcloud iam service-accounts keys create key/key.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
fi

# 作成した json 鍵を環境変数に反映
export GOOGLE_APPLICATION_CREDENTIALS=key/key.json
COMMENTOUT

# docker image を Cloud Build 上でビルドし、GCP Container Registry にアップロード
cd api/
gcloud builds submit --config cloudbuild.yml
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
