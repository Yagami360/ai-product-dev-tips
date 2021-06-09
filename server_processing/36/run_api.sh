#!/bin/sh
set -eu
HOST=0.0.0.0
PORT=5000
N_POLLING=15

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# リクエスト処理
python request.py --host ${HOST} --port ${PORT} --in_image_dir in_images --n_polling ${N_POLLING}

docker-compose logs --tail 50
#docker logs proxy-container