#!/bin/sh
set -eu

PROJECT_ID=my-project2-303004
REGION_ID=asia-northeast1-a
TOPIC_NAME=topic-sample
SUBSCRIPTION_NAME=sub-sample
CREDENTIALS_FILE_PATH="keys/my-project2-303004-deb769e4cb52.json"

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

# API 起動
docker-compose -f api/docker-compose.yml stop
docker-compose -f api/docker-compose.yml up -d

# リクエスト処理
sleep 1
python request.py --project_id ${PROJECT_ID} --sub_name ${SUBSCRIPTION_NAME} --credentials_file_path ${CREDENTIALS_FILE_PATH} --debug
