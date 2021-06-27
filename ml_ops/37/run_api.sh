#!/bin/sh
set -eu
HOST=0.0.0.0
PORT=5000

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# リクエスト処理
python request.py --host ${HOST} --port ${PORT} --in_images_dir in_images --out_images_dir out_images --debug

#docker logs fast-api-mysql-container
#docker logs batch-mysql-container
#docker logs mysql-container
