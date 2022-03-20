#!/bin/sh
set -eu

PROJECT_ID=my-project2-303004
TOPIC_NAME=export-logs-to-datadog
SUBSCRIPTION_NAME=datadog-sub
DATADOG_API_KEY=e22df3d0958810817576e2d94c0bedfb

# Cloud Pub/Sub 作成権限のある個人アカウントに変更
#gcloud auth login

# API を有効化する

# トピックを作成する
if [ ! "$(gcloud pubsub topics list | grep "name: projects/${PROJECT_ID}/topics/${TOPIC_NAME}")" ] ;then
    gcloud pubsub topics create ${TOPIC_NAME}
fi

gcloud pubsub topics list

# PUSH 型のサブスクリプション（受信側）を作成する
if [ ! "$(gcloud pubsub subscriptions list | grep "name: projects/${PROJECT_ID}/subscriptions/${SUBSCRIPTION_NAME}")" ] ;then
    gcloud pubsub subscriptions create ${SUBSCRIPTION_NAME} \
        --topic ${TOPIC_NAME} \
        --push-endpoint https://gcp-intake.logs.datadoghq.com/v1/input/${DATADOG_API_KEY} \
        --ack-deadline 10
fi

gcloud pubsub subscriptions list
