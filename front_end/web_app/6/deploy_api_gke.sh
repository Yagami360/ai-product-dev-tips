#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_ID=my-project2-303004
REGION=us-central1
ZONE=us-central1-b
#ZONE=us-central1-c

CPU_TYPE=n1-standard-1
GPU_TYPE=nvidia-tesla-t4
DISK_SIZE=64

CLUSTER_NAME=graph-cut-api-cluster

MIN_NODES=1
MAX_NODES=1

ENABLE_BUILD=0
#ENABLE_BUILD=1

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${REGION}
gcloud config list

# docker image を GCP の Container Registry にアップロード
if [ ! ${ENABLE_BUILD} = 0 ] ; then
    cd ${ROOT_DIR}/api
    gcloud builds submit --config cloudbuild.yml --timeout 3600
    cd ${ROOT_DIR}
fi

# クラスタを作成
if [ "$(gcloud container clusters list | grep "${CLUSTER_NAME}")" ] ; then
    gcloud container clusters delete ${CLUSTER_NAME} --region ${ZONE}
fi

gcloud container clusters create ${CLUSTER_NAME} \
    --region ${ZONE} \
    --num-nodes 1 \
    --machine-type ${CPU_TYPE} \
    --disk-size ${DISK_SIZE} \
    --scopes=gke-default,logging-write

# 作成したクラスタに切り替える
gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${ZONE} --project ${PROJECT_ID}

# k8s リソース（Pod, Service, HorizontalPodAutoscaler, configmap 等）の作成
kubectl apply -f k8s/graph_cut_api.yml

# 正常起動待ち
sleep 360
kubectl get pods
kubectl get service
kubectl get HorizontalPodAutoscaler

# 即座にスケールイン
kubectl scale deploy graph-cut-api-pod --replicas=1

# 作成した Pod のコンテナログを確認
kubectl logs `kubectl get pods | grep "graph-cut-api-pod" | awk '{print $1}'` graph-cut-api-container

# 作成した Pod のコンテナにアクセス
#kubectl exec -it `kubectl get pods | grep "graph-cut-api-pod" | awk '{print $1}'` /bin/bash
