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

# POST method でのリクエスト処理
echo "[POST method] predict\n"
curl -X POST -H "Content-Type: application/json" \
    -d '{"id":4, "name":"user4", "age":"100"}' \
    http://${HOST}:${PORT}/predict/
echo "\n"

# ログデータを取得
echo "[GET method] MySQL データベースの全ログデータを取得\n"
curl http://${HOST}:${PORT}/log_all
echo "\n"

echo "[GET method] MySQL データベースの最初のログデータを取得\n"
curl http://${HOST}:${PORT}/log_first
echo "\n"

#docker logs fast-api-mysql-container
#docker logs mysql-container
