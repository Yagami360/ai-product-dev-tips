#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004
REGION=asia-northeast1
ZONE=asia-northeast1-a

CLUSTER_NAME=api-cluster
CPU_TYPE=n1-standard-4

NUM_NODES=1
MIN_NODES=1
MAX_NODES=3

#ENABLE_BUILD=0
ENABLE_BUILD=1

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

gcloud beta container clusters create ${CLUSTER_NAME} \
    --region ${ZONE} \
    --machine-type ${CPU_TYPE} \
    --num-nodes ${NUM_NODES} \
    --min-nodes ${MIN_NODES} --max-nodes ${MAX_NODES} \
    --enable-autoscaling \
    --addons=Istio --istio-config=auth=MTLS_PERMISSIVE

#    --addons=Istio --istio-config=auth=MTLS_STRICT

# 作成した GKE クラスタに Istio が正常にインストールされているかを確認する
kubectl get pods -n istio-system
kubectl get service -n istio-system

# Istio の Envoy（プロキシサーバー）サイドカーを有効化する
kubectl label namespace default istio-injection=enabled

# ConfigMap を作成する
#kubectl apply -f k8s/configmap.yml

# Pod を作成する
kubectl apply -f k8s/deployment.yml
kubectl get pods

# Service を公開する
kubectl apply -f k8s/service.yml
kubectl get services

# DestinationRule を作成する
kubectl apply -f k8s/destination_rule.yml

# VirtualService を作成する
kubectl apply -f k8s/virtual_service.yml
sleep 60

# 作成した Pod のコンテナログを確認
kubectl logs `kubectl get pods | grep "predict-pod-a" | awk '{print $1}' | sed -n 1P` proxy-container-a
kubectl logs `kubectl get pods | grep "predict-pod-b" | awk '{print $1}' | sed -n 1P` predict-container-b

# 作成した Pod のコンテナにアクセス
#kubectl exec -it `kubectl get pods | grep "predict-pod-a" | awk '{print $1}' | sed -n 1P` /bin/bash
#kubectl exec -it `kubectl get pods | grep "predict-pod-b" | awk '{print $1}' | sed -n 1P` /bin/bash
