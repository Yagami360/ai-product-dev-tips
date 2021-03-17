#!/bin/sh
set -eu
CONTAINAER_NAME=flask-api-container
HOST=0.0.0.0
PORT=5000

if [ ! -e "api/open_ssl" ] ; then
    sh make_ssl_keys.sh
fi

# API 起動
docker-compose -f api/docker-compose.yml stop
docker-compose -f api/docker-compose.yml up -d

# リクエスト処理
python request.py --host ${HOST} --port ${PORT} --use_https --verify_ssl --debug
#docker logs ${CONTAINAER_NAME}

# ブラウザアクセス
open https://${HOST}:${PORT}
