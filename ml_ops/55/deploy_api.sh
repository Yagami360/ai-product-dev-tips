#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004

UPDATE_GCLOUD=0
ENABLE_BUILD=0

REGION=us-central1
ZONE=us-central1-b
CPU_TYPE=n1-standard-1
DISK_SIZE=64
CLUSTER_NAME=fast-api-rate-limit-cluster
NUM_NODES=1
MIN_NODES=1
MAX_NODES=1

SERVICE_ACCOUNT_NAME=cloud-armor-account
SECURITY_POLICY_NAME=rate-limit-policy
RATE_LIMIT_THRESHOLD_COUNT=10
RATE_LIMIT_INTERVAL_SEC=60

#-----------------------------------------------
# GCP 環境のデフォルト値の設定
#-----------------------------------------------
if [ ! ${UPDATE_GCLOUD} = 0 ] ; then
    sudo gcloud components update
fi
gcloud --version
gcloud config set project ${PROJECT_ID}
gcloud config list

#-----------------------------------------------
# Google Cloud Armor 用のサービスアカウントを作成する
#-----------------------------------------------
if [ ! -e "api/key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
    # サービスアカウント作成権限のある個人アカウントに変更
    gcloud auth login

    # サービスアカウントを作成する
    if [ ! "$(gcloud iam service-accounts list | grep ${SERVICE_ACCOUNT_NAME})" ] ;then
        gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME}
    fi

    # サービスアカウントに必要な権限（Google Cloud Armor セキュリティ ポリシーの IAM 権限）を付与する
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/compute.securityAdmin"
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/compute.networkAdmin"
    gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"

    # サービスアカウントの秘密鍵 (json) を生成する
    if [ ! -e "api/key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
        mkdir -p api/key
        gcloud iam service-accounts keys create api/key/${SERVICE_ACCOUNT_NAME}.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
    fi
fi

#-----------------------------------------------
# セキュリティポリシーの作成
#-----------------------------------------------
if [ "$(gcloud compute security-policies list | grep "${SECURITY_POLICY_NAME}")" ] ; then
    # すでにセキュリティポリシーが存在する場合は削除
    set +e
    gcloud compute security-policies delete ${SECURITY_POLICY_NAME}
    set -e
fi

if [ ! "$(gcloud compute security-policies list | grep "${SECURITY_POLICY_NAME}")" ] ; then
    # GKE のロードバランサーに適用するためのセキュリティポリシーを作成
    gcloud compute security-policies create ${SECURITY_POLICY_NAME} --description "rate-limit policy for GKE Load balancer"

    # セキュリティーポリシーのルール（RateLimit 制限）を作成する
    gcloud compute security-policies rules create 10 \
        --security-policy ${SECURITY_POLICY_NAME}    \
        --src-ip-ranges="*" \
        --action=throttle   \
        --rate-limit-threshold-count=${RATE_LIMIT_THRESHOLD_COUNT}  \
        --rate-limit-threshold-interval-sec=${RATE_LIMIT_INTERVAL_SEC}  \
        --conform-action=allow  \
        --exceed-action=deny-429    \
        --enforce-on-key=IP \
        --description "rate-limit rule"
    #    --src-ip-ranges="0.0.0.0/1" \
fi

#-----------------------------------------------
# GKE 版 API を構築する
#-----------------------------------------------
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
kubectl apply -f k8s/fast_api_rate_limit.yml

# セキュリティポリシーをバックエンドサービス（L7ロードバランサー）に接続する
#BACKEND_SERVICE_NAME="k8s2-um-btap4v85-default-fast-api-rate-limit-ingress-9r8cddkf"
#gcloud compute backend-services update ${BACKEND_SERVICE_NAME} --security-policy ${SECURITY_POLICY_NAME}

# 作成した Pod のコンテナログを確認
#kubectl logs `kubectl get pods | grep "fast-api-rate-limit-pod" | awk '{print $1}'`

# 作成した Pod のコンテナにアクセス
#kubectl exec -it `kubectl get pods | grep "fast-api-rate-limit-pod" | awk '{print $1}'` /bin/bash
