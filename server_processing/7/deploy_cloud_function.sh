#!/bin/sh
set -eu

PROJECT_ID=myproject-292103
FUNCTION_NAME=cloud-function-sample
REGION=us-central1
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
