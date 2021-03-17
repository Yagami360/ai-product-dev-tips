#!/bin/sh
set -eu

PROJECT_ID=my-project2-303004
REGION=us-central1
FUNCTION_NAME=cloud-function-gpu-sample
ENTORY_NAME=hello_world

# Cloud Function のデプロイ
gcloud functions deploy ${FUNCTION_NAME} \
    --region ${REGION} \
    --memory 256MB \
    --source src/ \
    --entry-point ${ENTORY_NAME} \
    --runtime python37 \
    --trigger-http

# Cloud Function の動作確認
curl -X POST https://${REGION}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME} -H "Content-Type: application/json" -d '{"message":"Hello Cloud functions"}'
