#!/bin/sh
set -eu
SERVICE_NAME=predict-server
HOST=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`
PORT=5001

IN_IMAGES_DIR=in_images
OUT_IMAGES_DIR=out_images
rm -rf ${OUT_IMAGES_DIR}

# リクエスト処理
python3 request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR}
