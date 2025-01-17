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
            -p 9100:9100 \
            -v "/:/host:ro,rslave" \
            prom/node-exporter:latest \
            --path.rootfs=/host

        # 自動起動有効化
        docker update --restart=always node-exporter
        ```

1. Slurm Exporter をインストールして起動する<br>

    - （公式の方法）パッケージでインストールする場合<br>
        docker pull ではインストールできないので、git clone して make する必要がある
        ```bash
        # https://github.com/vpenso/prometheus-slurm-exporter/blob/master/DEVELOPMENT.md
        # インストール
        git clone https://github.com/vpenso/prometheus-slurm-exporter.git
        cd prometheus-slurm-exporter
        make

        # 起動（フォワグラウンドで実行する場合）
        ./bin/prometheus-slurm-exporter

        # 起動（バックグラウンドで実行する場合）
        # nohup ./bin/prometheus-slurm-exporter &
        ```

    - （非公式）Docker コンテナでインストールする場合<br>
        非公式なのもあって、環境によっては動かない可能性大
        ```bash
        # インストール
        # https://github.com/dholt/prometheus-slurm-exporter
        docker pull dholt/prometheus-slurm-exporter:latest

        # 起動
        docker run -d --name slurm-exporter \
            --network="host" \
            -p 8080:8080 \
            -v /usr/bin/sdiag:/usr/bin/sdiag \
            -v /usr/bin/sinfo:/usr/bin/sinfo \
            -v /usr/bin/squeue:/usr/bin/squeue \
            -v /etc/slurm:/etc/slurm:ro \
            -v /usr/lib/slurm:/usr/lib/slurm:ro \
            -v /etc/hosts:/etc/hosts:ro \
            -v /var/run/munge:/var/run/munge:ro \
            dholt/prometheus-slurm-exporter:latest

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
            -p 9090:9090 \
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
            -p 3000:3000 \
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
            -p 9100:9100 \
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
        docker run -d --name dcgm-exporter \
            --network="host" \
            --pid="host" \
            -p 9400:9400 \
            --runtime=nvidia \
            --gpus all \
            nvidia/dcgm-exporter:latest

        # 自動起動有効化
        docker update --restart=always nvidia/dcgm-exporter
        ```

### ブラウザ上からの操作

1. （オプション）Prometheus の UI にアクセスする<br>
    疎通確認を兼ねて、Prometheus の UI にアクセスする
    ```bash
    http://0.0.0.0:9090
    ```
    <img width="500" alt="image" src="https://github.com/user-attachments/assets/28e8d1a4-286b-4810-a702-79cc8ba87f95" />
    <img width="500" alt="image" src="https://github.com/user-attachments/assets/38afe84b-300e-4c7c-bdcf-48582bc9fa94" />

1. Grafana の UI にアクセスする<br>
    ```bash
    http://0.0.0.0:3000
    ```
    初回は、ユーザー名（`admin`）とパスワード（`admin`）でログインできる

1. Grafana のダッシュボードを作成する<br>
    Grafana の UI 上からダッシュボードを作成する

    <img width="500" alt="image" src="https://github.com/user-attachments/assets/123bb8d1-d07d-456e-b7c0-7703c48bb7aa" /><br>
    <img width="500" alt="image" src="https://github.com/user-attachments/assets/5ee572a7-e0c1-4f90-b4eb-76eda96c800c" /><br>

    - Node Exporter のダッシュボード<br>
        「Import Dashboard」の画面で、[node-exporter-dashboard.json](./node-exporter-dashboard.json) を import する

        <img width="800" alt="image" src="https://github.com/user-attachments/assets/2146885b-c83f-412a-a6fe-622b5e40fa0e" />

        成功すると、以下のような Node Exporter で測定可能な「CPU」「メモリ」「ディスク」等のダッシュボードが作成される
        <img width="800" alt="image" src="https://github.com/user-attachments/assets/0f9ee5e1-2dbc-4613-b7a9-c5048e488ca2" /><br>

    - Slurm Exporter のダッシュボード<br>
        「Import Dashboard」の画面で、[slurm-exporter-dashboard.json](./slurm-exporter-dashboard.json) を import する

        <img width="800" alt="image" src="https://github.com/user-attachments/assets/aeddf084-3da6-4010-8692-174a2ff86239" />

    - NVIDIA DCGM Exporter のダッシュボード<br>
        「Import Dashboard」の画面で、[nvidia-dcgm-exporter-dashboard.json](./nvidia-dcgm-exporter-dashboard.json) を import する

        <img width="800" alt="image" src="https://github.com/user-attachments/assets/43e92b66-a351-42de-8ad7-23dfba2637bb" />

## 参考サイト

- https://qiita.com/dcm_miura-h/items/1e545f6cd486f27ecfaa
- https://zenn.dev/prage_negoya/articles/c9d023bffbf2a3