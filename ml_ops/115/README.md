# Grafana + Prometheus + NVIDIA DCGM Exporter を使用して、単一ノードのオンプレミス環境における GPU の駆動状況や Slurm での学習ジョブの予約＆実行状況を可視化する

## 方法（Ubuntu or Debian の場合）

1. NVIDIA DCGM [NVIDIA Data Center GPU Manager] をインストールする
    ```bash
    sudo apt-get install datacenter-gpu-manager
    ```

1. NVIDIA DCGM Exporter をインストールする
    ```bash
    # Install NVIDIA DCGM Exporter (Docker コンテナ内でインストール)
    docker pull nvidia/dcgm-exporter
    docker run -d --gpus all --rm -p 9400:9400 nvidia/dcgm-exporter
    ```

1. Prometheus をインストールする
    ```bash
    wget https://github.com/prometheus/prometheus/releases/download/v2.37.0/prometheus-2.37.0.linux-amd64.tar.gz
    tar xvfz prometheus-*.tar.gz
    cd prometheus-*
    ```
    > Prometheus : 時系列のテキストデータを扱うのが得意なデータベースを備えたオープンソースの監視システムソフトウェア

1. Prometheus を起動する
    ```bash
    # 設定ファイルを配置して起動
    cp prometheus.yml /etc/prometheus/
    ./prometheus --config.file=/etc/prometheus/prometheus.yml
    ```

1. Grafana をインストールする
    ```bash
    sudo apt-get install grafana
    ```

1. Grafana を起動する
    ```bash
    # 起動
    sudo systemctl start grafana-server

    # 自動起動有効化
    sudo systemctl enable grafana-server
    ```

## 参考サイト

- https://qiita.com/dcm_miura-h/items/1e545f6cd486f27ecfaa
