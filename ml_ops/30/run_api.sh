#!/bin/sh
set -eu
TAG_NAME=debug.test

# API を起動する
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

# Fluentd にログ送信
echo '{"log_message":"sample"}' | fluent-cat ${TAG_NAME}
