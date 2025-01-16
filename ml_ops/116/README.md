# Grafana + Prometheus + NVIDIA DCGM Exporter を使用して、マルチノードオンプレミス環境における GPU の駆動状況や Slurm での学習ジョブの予約や実行状況を可視化する

Slurm のマスターノードと計算ノードのマルチノードで構成される環境において、Grafana + Prometheus + NVIDIA DCGM Exporter を使用して、GPU の駆動状況や Slurm での学習ジョブの予約や実行状況を可視化する方法を記載する。

- Grafana<br>

- Prometheus<br>
    <img width="400" alt="image" src="https://github.com/user-attachments/assets/72eeea7a-aba3-4e82-870d-0a059e0b64e9" /><br>

    システムやアプリケーションの様々な指標を時系列データとして収集して、収集したメトリクスをローカルのタイムシリーズデータベースに保存したり、メトリクスをモニタリングしたり、アラートしたりするツール。<br>
    監視対象を Exporter として Docker Pull したコンテナでインストールするようになっており、監視対象が動的に変更されるようなスケーラブルな環境のリソース監視に向いている

    - Exporter<br>
        監視対象サーバー上で動かすプログラムで、監視対象のリソース毎に exporter が用意されている

        - Node Exporter<br>
            Linux サーバーの CPU、メモリ、ディスク使用率のメトリクスを監視するための Exporter

        - NVIDIA DCGM Exporter<br>
            Prometheus の Exporter の１つで、NVIDIA の GPU の駆動状況やパフォーマンスを監視するための Exporter

## 方法（Ubuntu or Debian の場合）

<img width="800" alt="image" src="https://github.com/user-attachments/assets/82c29c6e-1e26-4856-9915-ee1c6217e53a" />

マスターノード側に Prometheus と Grafana をインストールし、計算ノード側に NVIDIA DCGM Exporter をインストールする構成になる

### マスターノード側

1. Prometheus をインストールする
    ```bash
    wget https://github.com/prometheus/prometheus/releases/download/v2.37.0/prometheus-2.37.0.linux-amd64.tar.gz
    tar xvfz prometheus-*.tar.gz
    cd prometheus-*
    ```

1. Prometheus の設定ファイルを配置する
    ```bash
    cp prometheus.yml /etc/prometheus/
    ```

1. Grafana をインストールする
    ```bash
    sudo apt-get install grafana
    ```

1. Slurm Exporter をインストールする
    ```bash
    wget https://github.com/vpenso/prometheus-slurm-exporter/releases/download/v0.20/prometheus-slurm-exporter
    chmod +x prometheus-slurm-exporter
    ```

1. Slurm Exporter を起動する
    ```bash
    ./prometheus-slurm-exporter --listen-address=:8080
    ```

1. Prometheus を起動する
    ```bash
    # 起動
    sudo systemctl start prometheus

    # 自動起動有効化
    sudo systemctl enable prometheus
    ```

1. Grafana を起動する
    ```bash
    # 起動
    sudo systemctl start grafana-server

    # 自動起動有効化
    sudo systemctl enable grafana-server
    ```

### 計算ノード側

1. NVIDIA DCGM Exporter をインストールして起動する
    ```bash
    # Install NVIDIA DCGM [NVIDIA Data Center GPU Manager]
    sudo apt-get install datacenter-gpu-manager

    # Install NVIDIA DCGM Exporter
    # Prometheus の仕様として、Exporter は Docker Pull したコンテナでインストールするようになっている
    docker pull nvidia/dcgm-exporter
    docker run -d --gpus all --rm -p 9400:9400 nvidia/dcgm-exporter
    ```

## 参考サイト

- https://qiita.com/dcm_miura-h/items/1e545f6cd486f27ecfaa
