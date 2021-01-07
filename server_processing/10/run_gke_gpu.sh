#!/bin/sh
set -eu

PROJECT_ID=myproject-292103
REGION=asia-northeast1-a
IMAGE_NAME=sample-image
CLUSTER_NAME=sample-gpu-cluster
POOL_NAME=sample-gpu-pool
POD_NAME=sample-gpu-pod
SERVICE_NAME=sample-gpu-server
NUM_NODES=1
PORT=80
TARGET_PORT=80

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${REGION}
gcloud config list

# クラスタを作成
#gcloud container clusters create ${CLUSTER_NAME} \
#    --accelerator type=nvidia-tesla-t4,count=1

gcloud container clusters create ${CLUSTER_NAME} \
    --accelerator type=nvidia-tesla-t4,count=1

# GPU ノードプールを作成
gcloud container node-pools create ${POOL_NAME} \
    --accelerator type=nvidia-tesla-t4,count=1 \
    --cluster ${CLUSTER_NAME} \
    --num-nodes ${NUM_NODES} --min-nodes 0 --max-nodes ${NUM_NODES} \
    --enable-autoscaling \
    --machine-type n1-standard-4

<<COMMENTOUT
# docker image を GCP の Container Registry にアップロード
gcloud builds submit --config api/cloudbuild.yml

# Deployment を作成する
kubectl apply -f k8s/deployment.yml
kubectl get pods
kubectl get deployments

# Deployment を公開する
kubectl apply -f k8s/service.yml
kubectl get service ${SERVICE_NAME}

# 公開外部アドレス取得
sleep 10
EXTERNAL_IP=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`

# 公開外部アドレスにリクエスト処理して、レスポンスを受け取る
python request.py --host ${EXTERNAL_IP} --port ${PORT} --debug

# 公開外部アドレスの URL にアドレスして動作確認する
curl http://${EXTERNAL_IP}:${PORT}

# 作成した Pod のコンテナログを確認
POD_NAME_1=`kubectl get pods | awk '{print $1}' | sed -n 2p`
kubectl logs ${POD_NAME_1}

# 作成した Pod のコンテナにアクセス
kubectl exec -it ${POD_NAME_1} /bin/bash
COMMENTOUT