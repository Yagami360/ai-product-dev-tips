#!/bin/sh
#set -eu
PROJECT_ID=my-project2-303004
SERVICE_ACCOUNT_NAME=cloud-armor-account
CLUSTER_NAME=fast-api-cluster
REGION=us-central1

# GCE サービスアカウント -> API 用サービスアカウントへの切替え
export GOOGLE_APPLICATION_CREDENTIALS="/api/key/${SERVICE_ACCOUNT_NAME}.json"
gcloud auth activate-service-account ${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com --key-file /api/key/${SERVICE_ACCOUNT_NAME}.json
gcloud auth list

# 作成したクラスタに切り替える
gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${REGION} --project ${PROJECT_ID}
#kubectl get pods