#!/bin/sh
set -eu
IN_IMAGES_DIR=in_images

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# health check
echo "[GET method] ヘルスチェック\n"
curl http://0.0.0.0:5000/health
echo "\n"

# metadata 取得
echo "[GET method] metadata 取得\n"
curl http://0.0.0.0:5000/metadata
echo "\n"

# リクエスト処理
python request.py --host 0.0.0.0 --port 5000 --in_images_dir ${IN_IMAGES_DIR} --out_images_dir out_images1
python request.py --host 0.0.0.0 --port 5001 --in_images_dir ${IN_IMAGES_DIR} --out_images_dir out_images2

docker-compose logs --tail 50
