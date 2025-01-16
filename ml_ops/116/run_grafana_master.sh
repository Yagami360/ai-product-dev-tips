#!/bin/sh
set -eux

PROJECT_DIR=${PWD}

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
# Run Slurm Exporter
# -------------------------
# # インストール
# # https://github.com/vpenso/prometheus-slurm-exporter
# docker pull vpenso/prometheus-slurm-exporter:latest

# # 起動
# set +e
# docker rm -f slurm-exporter
# set -e

# docker run -d --name slurm-exporter \
#     --network="host" \
#     -p 8080:8080 \
#     -v /etc/slurm:/etc/slurm:ro \
#     -v /var/run/slurmctld.pid:/var/run/slurmctld.pid \
#     vpenso/prometheus-slurm-exporter:latest

# # 自動起動有効化
# docker update --restart=always slurm-exporter

# -------------------------
# Run Prometheus
# -------------------------
mkdir -p ${PROJECT_DIR}/prometheus

# インストール
docker pull prom/prometheus:latest

# 再起動（-v オプションでローカル環境上の設定ファイル prometheus.yml を /etc/prometheus に同期）
set +e
docker rm -f prometheus
set -e

docker run -d --name prometheus \
    --network="host" \
    -p 9090:9090 \
    -v ${PROJECT_DIR}/prometheus:/etc/prometheus \
    prom/prometheus:latest

# 自動起動有効化
docker update --restart=always prometheus

# -------------------------
# Run Grafana
# -------------------------
mkdir -p ${PROJECT_DIR}/grafana/data
mkdir -p ${PROJECT_DIR}/grafana/plugins

# 権限の設定 (Grafanaのデフォルトユーザー ID:472)
sudo chown -R 472:472 ${PROJECT_DIR}/grafana/data
sudo chown -R 472:472 ${PROJECT_DIR}/grafana/plugins

# インストール
docker pull grafana/grafana:latest

# 再起動
set +e
docker rm -f grafana
set -e

docker run -d --name grafana \
    --network="host" \
    -v ${PROJECT_DIR}/grafana/data:/var/lib/grafana/data \
    -v ${PROJECT_DIR}/grafana/plugins:/var/lib/grafana/plugins \
    grafana/grafana:latest

# docker run -d --name grafana \
#   -p 3000:3000 \
#   -v /opt/monitoring/grafana/data:/var/lib/grafana \
#   -v /opt/monitoring/grafana/plugins:/var/lib/grafana/plugins \
#   grafana/grafana:latest

# 自動起動有効化
docker update --restart=always grafana

# -------------------------
# Run Grafana Dashboard
# -------------------------
# open http://localhost:3000
