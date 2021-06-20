#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004
SERVICE_ACCOUNT_NAME=logging

HOST=0.0.0.0
PORT=5000

# Cloud logging でロギングを行うためのサービスアカウントを作成する
if [ ! "$(gcloud iam service-accounts list | grep ${SERVICE_ACCOUNT_NAME})" ] ;then
    gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME}
fi

# サービスアカウントにロギング権限を付与する
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/logging.logWriter"
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/monitoring.metricWriter"

# サービスアカウントの秘密鍵 (json) を生成する
if [ ! -e "key/key.json" ] ; then
    mkdir -p key
    gcloud iam service-accounts keys create key/key.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
fi

# 作成した json 鍵を環境変数に反映
export GOOGLE_APPLICATION_CREDENTIALS=key/key.json

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# health check
echo "[GET method] ヘルスチェック\n"
curl http://${HOST}:${PORT}/health
echo "\n"

# metadata 取得
echo "[GET method] metadata 取得\n"
curl http://${HOST}:${PORT}/metadata
echo "\n"

# POST method でのリクエスト処理
echo "[POST method] ユーザー追加\n"
curl -X POST -H "Content-Type: application/json" \
    -d '{"id":4, "name":"user4", "age":"100"}' \
    http://${HOST}:${PORT}/add_users/
echo "\n"

# Fluentd にログ送信
echo "Fluentd にログ送信\n"
echo '{"log_message":"sample"}' | fluent-cat debug
