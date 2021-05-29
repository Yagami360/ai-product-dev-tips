#!/bin/sh
set -eu

PROJECT_ID=my-project2-303004
REGION_ID=asia-northeast1-a
TOPIC_NAME=topic-sample
SUBSCRIPTION_NAME=sub-sample
CREDENTIALS_FILE_PATH="keys/my-project2-303004-deb769e4cb52.json"

# Pub/Sub の Python API をインストールする
pip install google-cloud-pubsub

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
#gcloud pubsub topics publish ${TOPIC_NAME} --message "Hello World!"

# トピックのメッセージを subscribe (pop) する
#gcloud pubsub subscriptions pull --auto-ack ${SUBSCRIPTION_NAME}

# 作成したサービスアカウントの json 鍵のファイルパスを環境変数に追加
#export GOOGLE_APPLICATION_CREDENTIALS="${CREDENTIALS_FILE_PATH}"

# パブリッシャーの Python スクリプトを実行する
python pub.py --project_id ${PROJECT_ID} --topic_name ${TOPIC_NAME} --credentials_file_path ${CREDENTIALS_FILE_PATH} &

# サブスクライバーの Python スクリプトを実行する
sleep 1
python sub.py --project_id ${PROJECT_ID} --sub_name ${SUBSCRIPTION_NAME} --credentials_file_path ${CREDENTIALS_FILE_PATH}
