#!/bin/sh
set -eu
HOST=localhost
PORT=6379
DATABASE_ID=0

# Redis サーバーの起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d

# Redis の Python API `redis-py` をインストールする
pip install redis

# Redis の Python スクリプトを実行
python hello_redis.py --host ${HOST} --port ${PORT} --database_id ${DATABASE_ID} --debug
