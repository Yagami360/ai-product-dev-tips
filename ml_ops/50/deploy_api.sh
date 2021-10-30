#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_ID=my-project2-303004
REGION=us-central1
ZONE=us-central1-b

CPU_TYPE=n1-standard-1
DISK_SIZE=64

CLUSTER_NAME=graph-cut-api-cluster

NUM_NODES=1
MIN_NODES=1
MAX_NODES=4

#ENABLE_BUILD=0
ENABLE_BUILD=1

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${REGION}
gcloud config list

# API用のサービスアカウント作成
bash make_service_account.sh

# docker image を GCP の Container Registry にアップロード
if [ ! ${ENABLE_BUILD} = 0 ] ; then
    gcloud builds submit --config cloudbuild.yml --timeout 3600
fi

# クラスタを作成
if [ "$(gcloud container clusters list | grep "${CLUSTER_NAME}")" ] ; then
    set +e
    gcloud container clusters delete ${CLUSTER_NAME} --region ${ZONE}
    set -e
fi

if [ ! "$(gcloud container clusters list | grep "${CLUSTER_NAME}")" ] ; then
  gcloud container clusters create ${CLUSTER_NAME} \
      --region ${ZONE} \
      --num-nodes ${NUM_NODES} \
      --machine-type ${CPU_TYPE} \
      --disk-size ${DISK_SIZE} \
      --enable-autoscaling --min-nodes ${MIN_NODES} --max-nodes ${MAX_NODES} \
      --scopes=gke-default,logging-write
fi

# 作成したクラスタに切り替える
gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${ZONE} --project ${PROJECT_ID}

# カスタム指標のためのアダプタ（Stackdriver Adapter） をデプロイ。 metric-server の Pod（custom-metrics-stackdriver-adapter） が起動
set +e
kubectl create clusterrolebinding cluster-admin-binding --clusterrole cluster-admin --user "$(gcloud config get-value account)"
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/k8s-stackdriver/master/custom-metrics-stackdriver-adapter/deploy/production/adapter.yaml
set -e

# k8s リソース（Pod, Service, HorizontalPodAutoscaler, configmap 等）の作成
kubectl apply -f k8s/redis.yml
kubectl apply -f k8s/predict.yml
kubectl apply -f k8s/proxy.yml
kubectl apply -f k8s/batch.yml
kubectl apply -f k8s/monitoring.yml

# 正常起動待ち
sleep 300
kubectl get pods
kubectl get service
kubectl get HorizontalPodAutoscaler

# 即座にスケールイン
kubectl scale deploy proxy-pod --replicas=1
kubectl scale deploy batch-pod --replicas=1
kubectl scale deploy monitoring-pod --replicas=1
kubectl scale deploy predict-pod --replicas=1

# 作成した Pod のコンテナログを確認
kubectl logs `kubectl get pods | grep "proxy-pod" | awk '{print $1}'` proxy-container
kubectl logs `kubectl get pods | grep "batch-pod" | awk '{print $1}'` batch-container
kubectl logs `kubectl get pods | grep "monitoring-pod" | awk '{print $1}'` monitoring-container
kubectl logs `kubectl get pods | grep "predict-pod" | awk '{print $1}'` predict-container

# 作成した Pod のコンテナにアクセス
#kubectl exec -it `kubectl get pods | grep "proxy-pod" | awk '{print $1}'` /bin/bash
#kubectl exec -it `kubectl get pods | grep "monitoring-pod" | awk '{print $1}'` /bin/bash