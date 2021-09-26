#!/bin/sh
set -eu
ROOT_DIR=${PWD}

PROJECT_ID=my-project2-303004
REGION=us-central1
ZONE=us-central1-b
#ZONE=us-central1-c

IP_ADDRESS_NAME=graph-cut-api-ip
DOMAINS="yagami360.com"
CERTIFICATE_NAME=graph-cut-api-ssl
INGRESS_NAME=graph-cut-api-ingress

CLUSTER_NAME=graph-cut-api-cluster
CPU_TYPE=n1-standard-4
GPU_TYPE=nvidia-tesla-t4

MIN_NODES=1
MAX_NODES=1

ENABLE_BUILD=0
#ENABLE_BUILD=1

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${REGION}
gcloud config list

#-------------------------------------
# ドメインの作成
#-------------------------------------

#-------------------------------------
# 固定 IP アドレス（グローバル）を取得する
#-------------------------------------
if [ ! "$(gcloud compute addresses list | grep "${IP_ADDRESS_NAME}")" ] ; then
    gcloud compute addresses create ${IP_ADDRESS_NAME} --global
    gcloud compute addresses describe ${IP_ADDRESS_NAME} --global
fi

#-------------------------------------
# Cloud DNS で IP アドレスとドメインを関連付ける
#-------------------------------------

#-------------------------------------
# Google マネージド SSL 証明書の作成
#-------------------------------------
# SSL 証明書を作成および変更できるための IAM 権限を設定する

# Google マネージド SSL 証明書の作成
if [ "$(gcloud compute ssl-certificates list | grep "${CERTIFICATE_NAME}")" ] ; then
    gcloud compute ssl-certificates delete ${CERTIFICATE_NAME}
fi

gcloud compute ssl-certificates create ${CERTIFICATE_NAME} \
    --description="graph-cut-api用SSL証明書" \
    --domains=${DOMAINS} \
    --global

#-------------------------------------
# クラスタを作成
#-------------------------------------
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

#-------------------------------------
# deployment と Service をクラスタに反映
#-------------------------------------
kubectl apply -f k8s/deployment.yml
#kubectl apply -f k8s/service_load_balancer.yml
kubectl apply -f k8s/service_node_port.yml
kubectl apply -f k8s/autoscale.yml
kubectl apply -f k8s/cert.yml
kubectl apply -f k8s/ingress.yml

# 正常起動待ち
sleep 360
kubectl get pods
kubectl get service
kubectl get HorizontalPodAutoscaler

# 即座にスケールイン
kubectl scale deploy graph-cut-api-pod --replicas=1

# 作成した Pod のコンテナログを確認
kubectl logs `kubectl get pods | grep "graph-cut-api-pod" | awk '{print $1}'` graph-cut-api-container

#-------------------------------------
# Google マネージド SSL 証明書を GKE のロードバランサのターゲットプロキシに関連付ける
#-------------------------------------
TARGET_PROXY_NAME=`gcloud compute target-https-proxies list | grep ${INGRESS_NAME} | awk -F" " '{print $1}'`

gcloud compute target-https-proxies update ${TARGET_PROXY_NAME} \
    --ssl-certificates ${CERTIFICATE_NAME} \
    --global-ssl-certificates \
    --global
    
#gcloud compute target-ssl-proxies update ${TARGET_PROXY_NAME} \
#    --ssl-certificates ${CERTIFICATE_NAME}

# ロードバランサーに関連付けられた SSL 証明書の確認
gcloud compute target-https-proxies describe ${TARGET_PROXY_NAME} \
    --global \
    --format="get(sslCertificates)"

# 作成した SSL 証明書が有効化（`ACTIVE`）されていることを確認
kubectl describe managedcertificate graph-cut-api-cert
