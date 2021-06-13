#!/bin/sh
set -eu
HOST=0.0.0.0
PORT=5000

IN_IMAGE_DIR=sample_n5
RESULTS_DIR=results
if [ -d "${RESULTS_DIR}" ] ; then
    rm -r ${RESULTS_DIR}
fi

# API 起動
docker-compose -f docker-compose_gpu.yml stop
docker-compose -f docker-compose_gpu.yml up -d
sleep 5

# リクエスト処理
curl http://${HOST}:${PORT}/health

python request.py \
    --host ${HOST} --port ${PORT} \
    --in_image_dir ${IN_IMAGE_DIR} \
    --results_dir ${RESULTS_DIR} \
    --debug

#docker-compose logs --tail 50
docker logs graphonomy-container-gpu
