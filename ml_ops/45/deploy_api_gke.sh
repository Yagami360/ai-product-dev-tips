#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_ID=my-project2-303004
REGION=us-central1
ZONE=us-central1-b
#ZONE=us-central1-c

CPU_TYPE=n1-standard-4
GPU_TYPE=nvidia-tesla-t4

IP_ADDRESS_NAME=graph-cut-api-ip
CERTIFICATE_NAME=graph-cut-api-ssl
DOMAINS="graph-cut-api.ga"
CLUSTER_NAME=graph-cut-api-cluster

MIN_NODES=1
MAX_NODES=1

ENABLE_BUILD=0
#ENABLE_BUILD=1

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${REGION}
gcloud config list

# 固定 IP アドレス（グローバル）を取得する
if [ ! "$(gcloud compute addresses list | grep "${IP_ADDRESS_NAME}")" ] ; then
    gcloud compute addresses create ${IP_ADDRESS_NAME} --global
    gcloud compute addresses describe ${IP_ADDRESS_NAME} --global
fi

# SSL 証明書を作成および変更できるための IAM 権限を設定する

# Google マネージド SSL 証明書の作成
if [ "$(gcloud compute ssl-certificates list | grep "${CERTIFICATE_NAME}")" ] ; then
    gcloud compute ssl-certificates delete ${CERTIFICATE_NAME}
fi

gcloud compute ssl-certificates create ${CERTIFICATE_NAME} \
    --description="graph-cut-api用SSL証明書" \
    --domains=${DOMAINS} \
    --global

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
    --num-nodes 1 \
    --machine-type ${CPU_TYPE} \
    --region ${ZONE} \
    --scopes=gke-default,logging-write

# 作成したクラスタに切り替える
gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${ZONE} --project ${PROJECT_ID}

# k8s リソース（Pod, Service, HorizontalPodAutoscaler, configmap 等）の作成
kubectl apply -f k8s/graph_cut_api.yml

# Google マネージド SSL 証明書を有効化する
TARGET_PROXY_NAME=`gcloud compute target-https-proxies list | grep ${CERTIFICATE_NAME} | awk -F" " '{print $1}'`

gcloud compute target-https-proxies update ${TARGET_PROXY_NAME} \
    --ssl-certificates ${CERTIFICATE_NAME} \
    --global-ssl-certificates \
    --global
    
#gcloud compute target-ssl-proxies update ${TARGET_PROXY_NAME} \
#    --ssl-certificates ${CERTIFICATE_NAME}

gcloud compute target-https-proxies describe ${TARGET_PROXY_NAME} \
    --global \
    --format="get(sslCertificates)"

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
