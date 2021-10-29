#!/bin/sh
set -eu
ROOT_DIR=${PWD}
SERVICE_NAME=graph-cut-api-server
HOST=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`
PORT=5000
N_POLLINGS=100

IN_IMAGES_DIR=in_images
OUT_IMAGES_DIR=out_images
rm -rf ${OUT_IMAGES_DIR}

# リクエスト処理
python3 request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR} --n_pollings ${N_POLLINGS}
