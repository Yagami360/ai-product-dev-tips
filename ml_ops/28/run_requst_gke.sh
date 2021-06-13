#!/bin/sh
set -eu
SERVICE_NAME=graphonomy-server
PORT=5000

IN_IMAGE_DIR=sample_n5
RESULTS_DIR=results_gke
if [ -d "${RESULTS_DIR}" ] ; then
    rm -r ${RESULTS_DIR}
fi

# 公開外部アドレス取得
EXTERNAL_IP=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`

# リクエスト処理
curl http://${EXTERNAL_IP}:${PORT}/health

python request.py \
    --host ${EXTERNAL_IP} --port ${PORT} \
    --in_image_dir ${IN_IMAGE_DIR} \
    --results_dir ${RESULTS_DIR} \
    --debug
