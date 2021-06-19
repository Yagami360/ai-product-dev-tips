#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004
REGION=asia-northeast1
ZONE=asia-northeast1-a

CLUSTER_NAME=fast-api-cluster
CPU_TYPE=n1-standard-4

NUM_NODES=1
MIN_NODES=1
MAX_NODES=1

ENABLE_BUILD=0
#ENABLE_BUILD=1

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}
gcloud config set compute/zone ${ZONE}
gcloud config list

# docker image を GCP の Container Registry にアップロード
if [ ! ${ENABLE_BUILD} = 0 ] ; then
    gcloud builds submit --config cloudbuild.yml
fi

# クラスタを作成
if [ "$(gcloud container clusters list | grep "${CLUSTER_NAME}")" ] ;then
    gcloud container clusters delete ${CLUSTER_NAME} --region ${ZONE}
fi

gcloud container clusters create ${CLUSTER_NAME} \
    --region ${ZONE} \
    --machine-type ${CPU_TYPE} \
    --cluster-version=1.4.10-gke.8 \
    --addons=Istio --istio-config=auth=MTLS_STRICT

#    --num-nodes ${NUM_NODES} \
#    --min-nodes ${MIN_NODES} --max-nodes ${MAX_NODES} \
#    --enable-autoscaling \

# ConfigMap を作成する
kubectl apply -f k8s/configmap.yml

# DestinationRule を作成する
kubectl apply -f k8s/destination_rule.yml

# Pod を作成する
kubectl apply -f k8s/deployment.yml

# Service を公開する
kubectl apply -f k8s/service.yml

# 作成した Pod のコンテナログを確認
#kubectl logs `kubectl get pods | grep "fast-api-pod" | awk '{print $1}'`

# 作成した Pod のコンテナにアクセス
#kubectl exec -it `kubectl get pods | grep "fast-api-pod" | awk '{print $1}'` /bin/bash
