#!/bin/sh
set -eux

# -------------------------
# Run Node Exporter
# -------------------------
# インストール
docker pull prom/node-exporter:latest

# 再起動
set +e
docker rm -f node-exporter
set -e

docker run -d --name node-exporter \
    --network="host" \
    --pid="host" \
    -p 9100:9100 \
    -v "/:/host:ro,rslave" \
    prom/node-exporter:latest \
    --path.rootfs=/host

# 自動起動有効化
docker update --restart=always node-exporter

# -------------------------
# Run Nvidia DCGM Exporter
# -------------------------
# インストール
docker pull nvidia/dcgm-exporter:latest

# 再起動
set +e
docker rm -f dcgm-exporter
set -e

docker run -d --name dcgm-exporter \
    --network="host" \
    --pid="host" \
    -p 9400:9400 \
    --runtime=nvidia \
    --gpus all \
    nvidia/dcgm-exporter:latest

# 自動起動有効化
docker update --restart=always dcgm-exporter
