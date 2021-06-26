#!/bin/sh
set -eu

# PyMySQL をインストールする
if [ ! "$(pip list | grep PyMySQL)" ] ; then
    pip install PyMySQL
fi 

# SQLAlchemy をインストールする
if [ ! "$(pip list | grep SQLAlchemy)" ] ; then
    pip install sqlalchemy
fi

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# Python スクリプトの実行
python crud.py --debug
