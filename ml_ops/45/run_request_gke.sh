#!/bin/sh
set -eu
ROOT_DIR=${PWD}
SERVICE_NAME=graph-cut-api-server
#HOST=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`
HOST=34.149.113.28
PORT=5000
TIMEOUT_CONNECT=3600
TIMEOUT_READ=3600

IN_IMAGES_DIR=sample_n5             # 入力ディレクトリ
OUT_IMAGES_DIR=out_images           # 出力ディレクトリ

# ヘルスチェック
curl http://${HOST}:${PORT}/health
curl https://${HOST}:${PORT}/health

# リクエスト処理
python request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR}
#python request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR} --use_https
