#!/bin/sh
set -eu

#=============================
# PostgreSQL
#=============================
# PostgreSQL サーバーに接続する
docker exec -it postgresql-container /bin/bash -c "psql -h localhost -U postgres"
