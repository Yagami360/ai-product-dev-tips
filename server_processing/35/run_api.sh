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
curl -X POST http://${HOST}:${PORT}/start_job/0?n_steps=100
echo "\n"
curl -X POST http://${HOST}:${PORT}/start_job/1?n_steps=10
echo "\n"
curl -X POST http://${HOST}:${PORT}/start_job/2?n_steps=20
echo "\n"

# ジョブ中断
curl -X POST http://${HOST}:${PORT}/stop_job/0
echo "\n"
curl http://${HOST}:${PORT}/metadata
echo "\n"

# ポーリング処理
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

docker-compose logs --tail 50