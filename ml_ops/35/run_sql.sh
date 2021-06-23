#!/bin/sh
set -eu

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d

# Python スクリプトの実行
python main.py --debug
