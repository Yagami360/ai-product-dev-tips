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
#docker run --rm -it  -p 3306:3306/tcp -p 33060:33060/tcp mysql:5.7 /bin/bash
docker logs mysql-container

# Python スクリプトの実行
#python main.py --debug
