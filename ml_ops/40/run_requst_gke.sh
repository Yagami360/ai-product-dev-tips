#!/bin/sh
set -eu
SERVICE_NAME=proxy-server
HOST=`kubectl get services | grep ${SERVICE_NAME} | awk '{print $4}'`
PORT=5000
IN_IMAGES_DIR=in_images

# health check
echo "[GET method] ヘルスチェック\n"
curl http://${HOST}:${PORT}/health
echo "\n"

# metadata 取得
echo "[GET method] metadata 取得\n"
curl http://${HOST}:${PORT}/metadata
echo "\n"

# リクエスト処理
python request.py --host ${HOST} --port ${PORT} --headers_target_value "condition1" --in_images_dir ${IN_IMAGES_DIR} --out_images_dir out_images1
python request.py --host ${HOST} --port ${PORT} --headers_target_value "condition2" --in_images_dir ${IN_IMAGES_DIR} --out_images_dir out_images2
