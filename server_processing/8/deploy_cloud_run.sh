#!/bin/sh
set -eu

IMAGE_NAME=sample_image
PROJECT_ID=my-project2-303004
SERVICE_NAME=cloud-run-sample
REGION=us-central1
PORT=8080
HOST_ADRESS=https://${SERVICE_NAME}-zilzej7vmq-uc.a.run.app

# 1. docker image を作成
#docker build -t gcr.io/${PROJECT_ID}/${IMAGE_NAME} .

# 2. 作成した docker image を GCP の Container Registry にアップロード
#docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}
gcloud builds submit --tag gcr.io/${PROJECT_ID}/${IMAGE_NAME}

# 3. アップロードした docker image を元に Cloud Run を作成する（=docker image を Cloud Run にデプロイ）
gcloud beta run deploy ${SERVICE_NAME} --image gcr.io/${PROJECT_ID}/${IMAGE_NAME} --region=${REGION}

# 4. Cloud Run の動作確認
curl -H "Content-type: application/json"  -X POST -d "{\"name\":\"test\"}"  ${HOST_ADRESS}:${PORT}/hello_world
