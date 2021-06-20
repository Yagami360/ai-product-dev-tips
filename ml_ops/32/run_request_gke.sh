#!/bin/sh
set -eu
SERVICE_NAME=fast-api-server
EXTERNAL_IP=`kubectl get services | grep ${SERVICE_NAME} | awk '{print $4}'`
PORT=5000

# health check
echo "[GET method] ヘルスチェック\n"
curl http://${EXTERNAL_IP}:${PORT}/health
echo "\n"

# metadata 取得
echo "[GET method] metadata 取得\n"
curl http://${EXTERNAL_IP}:${PORT}/metadata
echo "\n"

# POST method でのリクエスト処理
echo "[POST method] ユーザー追加\n"
curl -X POST -H "Content-Type: application/json" \
    -d '{"id":4, "name":"user4", "age":"100"}' \
    http://${EXTERNAL_IP}:${PORT}/add_users/
echo "\n"

# 作成した Pod のコンテナログを確認
#kubectl logs `kubectl get pods | grep "fast-api-pod" | awk '{print $1}'` fast-api-container
#kubectl logs `kubectl get pods | grep "fast-api-pod" | awk '{print $1}'` fluentd-container

# 作成した Pod のコンテナにアクセス
#kubectl exec -it `kubectl get pods | grep "fast-api-pod" | awk '{print $1}'` /bin/bash

