#!/bin/sh
set -eu

#=============================
# PostgreSQL
#=============================
rm -rf postgresql/db
mkdir -p postgresql/db

# PostgreSQL サーバー起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
#sleep 15

# PostgreSQL サーバーに接続する
#docker exec -it postgresql-container /bin/bash -c "psql -h localhost -U postgres"
