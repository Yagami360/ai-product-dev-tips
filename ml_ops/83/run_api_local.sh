#!/bin/sh
set -eu

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# health check
echo "[GET method] ヘルスチェック\n"
curl http://0.0.0.0:5000/health
echo "\n"
