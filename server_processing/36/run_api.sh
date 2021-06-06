#!/bin/sh
set -eu
HOST=0.0.0.0
PORT=5000
N_POLLING=15

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

# ジョブ開始
curl -X POST http://${HOST}:${PORT}/start_job/
echo "\n"
curl -X POST http://${HOST}:${PORT}/start_job/
echo "\n"
curl -X POST http://${HOST}:${PORT}/start_job/
echo "\n"

# ポーリング処理
<<COMMENTOUT
for i in `seq ${N_POLLING}`
do
    curl -X GET http://${HOST}:${PORT}/get_job/0
    echo "\n"
    curl -X GET http://${HOST}:${PORT}/get_job/1
    echo "\n"
    curl -X GET http://${HOST}:${PORT}/get_job/2
    echo "\n"
    sleep 1
done
COMMENTOUT

docker-compose logs --tail 10
