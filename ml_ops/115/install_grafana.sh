#!/bin/sh
set -eu
PROJECT_DIR=$(cd $(dirname $0)/..; pwd)
PROMETHEUS_VERSION=2.37.0

lsb_release -a

sudo apt update

# Install NVIDIA DCGM [NVIDIA Data Center GPU Manager]
sudo apt-get install datacenter-gpu-manager

# NVIDIA DCGM Exporter
docker pull nvidia/dcgm-exporter
docker run -d --gpus all --rm -p 9400:9400 nvidia/dcgm-exporter

# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.37.0/prometheus-2.37.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Start Prometheus
./prometheus --config.file=/etc/prometheus/prometheus.yml

# Install Grafana
sudo apt-get install grafana

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
