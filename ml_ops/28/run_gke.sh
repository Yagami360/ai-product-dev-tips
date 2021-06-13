#!/bin/sh
set -eu

PROJECT_ID=my-project2-303004

REGION=asia-northeast1
#REGION=us-central1
ZONE=asia-northeast1-a
#ZONE=us-central1-c

CPU_TYPE=n1-standard-4
if [ ${ZONE} = "us-central1-c" ] ; then
    GPU_TYPE=nvidia-tesla-k80
else
    GPU_TYPE=nvidia-tesla-t4
fi

CLUSTER_NAME=graphonomy-cluster
POD_NAME=graphonomy-pod
SERVICE_NAME=graphonomy-server

N_GPUS=1
MIN_NODES=1
MAX_NODES=1

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

# GPU ノードプールを作成
gcloud container node-pools create ${POOL_NAME} \
    --cluster ${CLUSTER_NAME} \
    --region ${ZONE} \
    --machine-type ${CPU_TYPE} \
    --accelerator type=${GPU_TYPE},count=${N_GPUS} \
    --min-nodes ${MIN_NODES} --max-nodes ${MAX_NODES} \
    --enable-autoscaling

# k8s の DaemonSet での Pod 経由で GPU ドライバーをインストール
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
sleep 180
kubectl get pods -n=kube-system

# API の Pod を作成する
kubectl apply -f api/k8s/deployment.yml

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
