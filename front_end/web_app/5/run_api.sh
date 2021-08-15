#!/bin/sh
set -eu
HOST=0.0.0.0
PORT=5000

IN_IMAGES_DIR=public/sample_n5
OUT_IMAGES_DIR=out_images
rm -rf ${OUT_IMAGES_DIR}

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# ヘルスチェック
curl http://${HOST}:${PORT}/health

# リクエスト処理
python request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR}
