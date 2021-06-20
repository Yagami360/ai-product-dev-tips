#!/bin/sh
set -eu
SERVICE_NAME=fast-api-server
EXTERNAL_IP=`kubectl get services | grep ${SERVICE_NAME} | awk '{print $4}'`
PORT=5000

# 公開外部アドレスの URL にアドレスして動作確認する
echo "[GET method] ヘルスチェック\n"
curl http://${EXTERNAL_IP}:${PORT}/health
echo "\n"

echo "[GET method] metadata 取得\n"
curl http://${EXTERNAL_IP}:${PORT}/metadata
echo "\n"

echo "[GET method] パスパラメーターで指定\n"
curl http://${EXTERNAL_IP}:${PORT}/users_name/0
curl http://${EXTERNAL_IP}:${PORT}/users_name/1
curl http://${EXTERNAL_IP}:${PORT}/users_name/2
echo "\n"

echo "[GET method] クエリパラメーターで指定\n"
curl http://${EXTERNAL_IP}:${PORT}/users_name/?users_id=0
curl http://${EXTERNAL_IP}:${PORT}/users_name/?users_id=1
curl http://${EXTERNAL_IP}:${PORT}/users_name/?users_id=2
echo "\n"

# POST method でのリクエスト処理
echo "[POST method] ユーザー追加\n"
curl -X POST -H "Content-Type: application/json" \
    -d '{"id":4, "name":"user4", "age":"100"}' \
    http://${EXTERNAL_IP}:${PORT}/add_users/

echo "\n"