#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_ID=my-project2-303004
REGION=us-central1
ZONE=us-central1-b

CPU_TYPE=n1-standard-1
DISK_SIZE=64

CLUSTER_NAME=sample-job-cluster

NUM_NODES=1
MIN_NODES=1
MAX_NODES=4

#ENABLE_BUILD=0
ENABLE_BUILD=1

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${REGION}
gcloud config list

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

# k8s リソース（Pod, Service, HorizontalPodAutoscaler, configmap 等）の作成
kubectl apply -f k8s/job.yml
#kubectl delete job $(kubectl get job -o custom-columns=:.metadata.name)

# 正常起動待ち
sleep 30
kubectl get pods
kubectl get job

# 作成した Pod のコンテナログを確認
#kubectl logs `kubectl get pods | grep "predict-pod" | awk '{print $1}'` predict-container

# 作成した Pod のコンテナにアクセス
#kubectl exec -it `kubectl get pods | grep "predict-pod" | awk '{print $1}'` /bin/bash
