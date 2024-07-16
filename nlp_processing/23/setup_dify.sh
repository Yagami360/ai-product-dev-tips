#!/bin/bash
set -eu
PROJECT_DIR=$(cd $(dirname $0)/..; pwd)

# install dify on local
if [ ! -d "dify" ]; then
    git clone https://github.com/langgenius/dify.git
fi

cd ${PROJECT_DIR}/dify/docker

# setup dify environment
if [ ! -f .env ] &&
    cp .env.example .env
fi

# run dify containers
docker-compose up -d

# open dify web
open http://localhost/install
