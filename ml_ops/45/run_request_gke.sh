#!/bin/sh
set -eu
ROOT_DIR=${PWD}
USE_HTTPS=1

HOST=34.149.113.28
if [ ${USE_HTTPS} = 0 ] ; then
    PORT=80
else
    PORT=443
fi

TIMEOUT_CONNECT=3600
TIMEOUT_READ=3600


IN_IMAGES_DIR=sample_n5             # 入力ディレクトリ
OUT_IMAGES_DIR=out_images           # 出力ディレクトリ

# ヘルスチェック
if [ ${USE_HTTPS} = 0 ] ; then
    curl http://${HOST}:${PORT}/health
else
    curl https://${HOST}:${PORT}/health
fi

# リクエスト処理
if [ ${USE_HTTPS} = 0 ] ; then
    python request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR}
else
    python request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR} --use_https
fi