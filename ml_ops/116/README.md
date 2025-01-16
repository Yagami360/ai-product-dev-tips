# Grafana + Prometheus + NVIDIA DCGM Exporter を使用して、マルチノードオンプレミス環境における GPU の駆動状況や Slurm での学習ジョブの予約や実行状況を可視化する

Slurm のマスターノードと計算ノードのマルチノードで構成される環境において、Grafana + Prometheus + NVIDIA DCGM Exporter を使用して、GPU の駆動状況や Slurm での学習ジョブの予約や実行状況を可視化する方法を記載する。

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

- Grafana<br>
    Prometheus や Elasticsearch 等で収集したメトリクスを可視化するためのツール。
    Prometheus のデフォルトの可視化 GUI だと非常に見た目がしょぼくて機能も少ないが、Grafana を使用することでより見やすく、機能も豊富になる。

## 方法（Ubuntu or Debian の場合）

<img width="800" alt="image" src="https://github.com/user-attachments/assets/516191ef-4659-4ed9-81b4-5ad6eb4d5be3" />

マスターノード側に Prometheus と Grafana をインストールし、計算ノード側に NVIDIA DCGM Exporter をインストールして起動する構成になる

### マスターノード側

1. サーバーのホスト名を設定する<br>
    `prometheus.yml` で定義するホスト名の名前解決を行うため、`/etc/hosts` を編集する
    ```bash
    sudo vi /etc/hosts
    ```

    `/etc/hosts` に以下の行を追加する
    ```
    <マスターノードのIPアドレス（内部IP）>    server-a（マスターノードのホスト名）
    <計算ノードのIPアドレス（内部IP）>    server-b（計算ノードのホスト名）
    ```

1. ポートを開放する<br>
    ファイアウォールで `prometheus.yml` で定義したポートを開放し、相互に通信できるようにする

    - GCE の場合<br>
        1. VPCネットワーク → ファイアウォール → ファイアウォールルールを作成
            - 名前: `allow-prometheus-master`
            - ターゲットタグ: `prometheus-master`（または適切なタグ）
            - ソースIPの範囲: `xx.xxx.0.0/16`（マスターノードと計算ノードの内部IPの範囲になるように指定）
            - プロトコルとポート:
                - prometheus 用
                    - `tcp:9100` : Node Exporter
                    - `tcp:9400` : NVIDIA DCGM Exporter
                    - `tcp:8080` : Slurm Exporter
                - Grafana 用
                    - `tcp:3000`
                - ping での疎通確認用
                    - `icmp`

        1. GCE インスタンスのネットワークタグに `prometheus-master` を追加する

1. Prometheus の設定ファイル（`prometheus.yml`）を作成する
    ```bash
    mkdir -p ${HOME}/monitoring/prometheus
    cat << EOF > ${HOME}/monitoring/prometheus/prometheus.yml
    global:
        scrape_interval: 15s
        evaluation_interval: 15s

    scrape_configs:
    # Node Exporter
    - job_name: 'node'
        static_configs:
        - targets: ['server-a:9100', 'server-b:9100']

    # DCGM Exporter
    - job_name: 'dcgm'
        static_configs:
        - targets: ['server-b:9400']
            labels:
            instance: 'server-b'

    # Slurm Exporter
    - job_name: 'slurm'
        static_configs:
        - targets: ['server-a:8080']
            labels:
            instance: 'server-a'
    EOF
    ```

1. Node Exporter をインストールして起動する<br>

    - Docker コンテナでインストールする場合<br>
        ```bash
        # インストール
        docker pull prom/node-exporter:latest

        # 起動
        docker run -d --name node-exporter \
            --network="host" \
            --pid="host" \
            -v "/:/host:ro,rslave" \
            prom/node-exporter:latest \
            --path.rootfs=/host

        # 自動起動有効化
        docker update --restart=always node-exporter
        ```

1. Slurm Exporter をインストールして起動する<br>

    - Docker コンテナでインストールする場合<br>
        ```bash
        # インストール
        # https://github.com/vpenso/prometheus-slurm-exporter
        docker pull vpenso/prometheus-slurm-exporter:latest

        # 起動
        docker run -d --name slurm-exporter \
            --network="host" \
            -v /etc/slurm:/etc/slurm:ro \
            -v /var/run/slurmctld.pid:/var/run/slurmctld.pid \
            vpenso/prometheus-slurm-exporter:latest

        # 自動起動有効化
        docker update --restart=always slurm-exporter
        ```

1. Prometheus をインストールして起動する

    - Docker コンテナでインストールする場合<br>
        ```bash
        # インストール
        docker pull prom/prometheus:latest

        # 起動（-v オプションでローカル環境上の設定ファイル prometheus.yml を /etc/prometheus に同期）
        docker run -d --name prometheus \
            --network="host" \
            -v ${HOME}/monitoring/prometheus:/etc/prometheus \
            prom/prometheus:latest

        # 自動起動有効化
        docker update --restart=always prometheus
        ```

<!-- 1. Prometheus の UI にアクセスする<br>
    ```bash
    http://server-a:9090
    ```
-->

1. Grafana をインストールして起動する

    - Docker コンテナでインストールする場合<br>
        ```bash
        # データディレクトリの作成
        mkdir -p ${HOME}/monitoring/grafana/data
        mkdir -p ${HOME}/monitoring/grafana/plugins

        # 権限の設定 (Grafanaのデフォルトユーザー ID:472)
        sudo chown -R 472:472 ${HOME}/monitoring/grafana/data
        sudo chown -R 472:472 ${HOME}/monitoring/grafana/plugins

        # インストール
        docker pull grafana/grafana:latest

        # 起動
        docker run -d --name grafana \
            --network="host" \
            -v ${HOME}/monitoring/grafana/data:/var/lib/grafana/data \
            -v ${HOME}/monitoring/grafana/plugins:/var/lib/grafana/plugins \
            grafana/grafana:latest

        # 自動起動有効化
        docker update --restart=always grafana
        ```

    - パッケージでインストールする場合<br>  
        ```bash
        # インストール
        wget https://dl.grafana.com/oss/release/grafana-10.0.0.linux-amd64.tar.gz
        tar -zxvf grafana-10.0.0.linux-amd64.tar.gz
        mv grafana-10.0.0 grafana

        # 起動
        sudo systemctl start grafana-server

        # 自動起動有効化
        sudo systemctl enable grafana-server
        ```

1. Grafana の UI にアクセスする<br>
    ```bash
    http://${外部IPアドレス}:3000
    ```

### 計算ノード側

1. サーバーのホスト名を設定する<br>
    `prometheus.yml` で定義するホスト名の名前解決を行うため、`/etc/hosts` を編集する
    ```bash
    sudo vi /etc/hosts
    ```

    `/etc/hosts` に以下の行を追加する
    ```
    <マスターノードのIPアドレス（内部IP）>    server-a（マスターノードのホスト名）
    <計算ノードのIPアドレス（内部IP）>    server-b（計算ノードのホスト名）
    ```

1. ポートを開放する<br>
    ファイアウォールで `prometheus.yml` で定義したポートを開放し、相互に通信できるようにする

    - GCE の場合<br>
        1. VPCネットワーク → ファイアウォール → ファイアウォールルールを作成
            - 名前: `allow-prometheus-worker`
            - ターゲットタグ: `prometheus-worker`（または適切なタグ）
            - ソースIPの範囲: `xx.xxx.0.0/16`（マスターノードと計算ノードの内部IPの範囲になるように指定）
            - プロトコルとポート:
                - prometheus 用
                    - `tcp:9100` : Node Exporter
                    - `tcp:9400` : NVIDIA DCGM Exporter
                - ping での疎通確認用
                    - `icmp`

        1. GCE インスタンスのネットワークタグに `prometheus-worker` を追加する

1. Node Exporter をインストールして起動する<br>

    - Docker コンテナでインストールする場合<br>
        ```bash
        # インストール
        docker pull prom/node-exporter:latest

        # 起動
        docker run -d --name node-exporter \
            --network="host" \
            --pid="host" \
            -v "/:/host:ro,rslave" \
            prom/node-exporter:latest \
            --path.rootfs=/host

        # 自動起動有効化
        docker update --restart=always node-exporter
        ```

1. NVIDIA DCGM Exporter をインストールして起動する<br>

    - Docker コンテナでインストールする場合<br>
        ```bash
        # インストール
        docker pull nvidia/dcgm-exporter

        # 起動
        docker run -d --gpus all --rm -p 9400:9400 nvidia/dcgm-exporter

        # 自動起動有効化
        docker update --restart=always nvidia/dcgm-exporter
        ```

## 参考サイト

- https://qiita.com/dcm_miura-h/items/1e545f6cd486f27ecfaa
