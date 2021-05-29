#!/bin/sh
set -eu

PROJECT_ID=my-project2-303004
REGION_ID=asia-northeast1-a
TOPIC_NAME=topic-sample
SUBSCRIPTION_NAME=sub-sample

# API を有効化

# トピックを作成する
if [ ! "$(gcloud pubsub topics list | grep "name: projects/${PROJECT_ID}/topics/${TOPIC_NAME}")" ] ;then
    gcloud pubsub topics create ${TOPIC_NAME}
fi

gcloud pubsub topics list

# サブスクリプション（受信側）を作成する
if [ ! "$(gcloud pubsub subscriptions list | grep "name: projects/${PROJECT_ID}/subscriptions/${SUBSCRIPTION_NAME}")" ] ;then
    gcloud pubsub subscriptions create ${SUBSCRIPTION_NAME} \
        --topic ${TOPIC_NAME} \
        --ack-deadline 10
fi

gcloud pubsub subscriptions list

# トピックにメッセージを publish する
gcloud pubsub topics publish ${TOPIC_NAME} --message "Hello World!"

# トピックのメッセージを subscribe (pop) する
gcloud pubsub subscriptions pull --auto-ack ${SUBSCRIPTION_NAME}
