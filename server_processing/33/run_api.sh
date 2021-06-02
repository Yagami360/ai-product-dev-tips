#!/bin/sh
set -eu
HOST=0.0.0.0
PORT=5000

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d

# リクエスト処理を送信
sleep 5
echo "FastAPI サーバーにアクセス"
curl http://${HOST}:${PORT}

docker-compose logs