#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_ID=my-project2-303004
HOST=0.0.0.0
PORT=5000
N_POLLINGS=100

IN_IMAGES_DIR=in_images
OUT_IMAGES_DIR=out_images
rm -rf ${OUT_IMAGES_DIR}

# GCS デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config list

# Monitoring API を有効化
gcloud services enable monitoring

# サービスアカウントを作成
bash make_service_account.sh

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# リクエスト処理
python3 request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR} --n_pollings ${N_POLLINGS}

#docker-compose logs --tail 50
#docker logs proxy-container
#docker logs monitoring-container
