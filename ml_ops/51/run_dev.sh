#!/bin/sh
set -eu
ROOT_DIR=${PWD}
HOST=0.0.0.0
PORT=5000

# 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d

