#!/bin/sh
set -eu
HOST=0.0.0.0
PORT=5000

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

# GET method でのリクエスト処理
echo "[GET method] パスパラメーターで指定\n"
curl http://${HOST}:${PORT}/users_name/0
curl http://${HOST}:${PORT}/users_name/1
curl http://${HOST}:${PORT}/users_name/2
echo "\n"

echo "[GET method] クエリパラメーターで指定\n"
curl http://${HOST}:${PORT}/users_name/?users_id=0
curl http://${HOST}:${PORT}/users_name/?users_id=1
curl http://${HOST}:${PORT}/users_name/?users_id=2
echo "\n"

echo "[GET method] パスパラメーター & クエリパラメーターで指定\n"
curl http://${HOST}:${PORT}/users/name?users_id=0
curl http://${HOST}:${PORT}/users/age?users_id=0
curl http://${HOST}:${PORT}/users/name?users_id=1
curl http://${HOST}:${PORT}/users/age?users_id=1
curl http://${HOST}:${PORT}/users/name?users_id=2
curl http://${HOST}:${PORT}/users/age?users_id=2
echo "\n"

# POST method でのリクエスト処理
echo "[POST method] ユーザー追加\n"
curl -X POST -H "Content-Type: application/json" \
    -d '{"id":4, "name":"user4", "age":"100"}' \
    http://${HOST}:${PORT}/add_users/

echo "\n"

docker-compose logs --tail 50