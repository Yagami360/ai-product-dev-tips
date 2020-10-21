# 【GCP】GKE [Google Kubernetes Engine] の基本事項

## ■ GKE の基本事項

<img src="https://user-images.githubusercontent.com/25688193/96675747-9168de80-13a6-11eb-9614-f93679137e47.png" width="500">

- Node : Dockerが動くマシンのこと。
- Pod : コンテナを配置する入れ物で１つ以上のコンテナを持つ。この単位でスケーリングされる。
- Proxy : コンテナとの通信を経由するプロキシ。
- Deployments : Pod（コンテナ）を複数集めて管理するもの。
- Service : Deployment に対して外部からアクセス可能な IP アドレスを付与し、外部からアクセスできるようにしたもの

### ◎ 参考サイト
- https://cloud.google.com/kubernetes-engine/docs/quickstart#dockerfile
- https://qiita.com/ntoreg/items/74aa6de2f8f29b4a3b79
- https://www.topgate.co.jp/gcp07-how-to-start-docker-image-gke

## ■ GKE の構築手順

0. 【事前準備】作成した api コードの docker image を作成し、GCP の Container Registry にアップロード
1. クラスタを作成
1. クラスタの認証情報を取得
1. Deployment を作成する（＝作成したクラスタに、コンテナ化された docker image をデプロイする）
1. Deployment を公開する
1. 公開サイトにアクセスして動作確認する

### 1. クラスタを作成

#### ☆ GUI 使用時
[GKE の GUI 画面上](https://console.cloud.google.com/kubernetes/list?project=myproject-292103&folder&organizationId) から作成できる

#### ☆ GUI 非使用時

- クラスタを作成
    ```sh
    $ gcloud container clusters create ${CLUSTER_NAME} --num-nodes=
    ```
    - `${CLUSTER_NAME}` : 作成するクラスターの名前（`_` は使用できないことに注意）
    - `--nodes` : ノード数（デフォルトでは３）

<!--
- Kubernetes のローカルプロキシを起動
    上記コマンドでクラスターを作成した時点で、既にKubernetesも起動しているので、以下のコマンドでローカルプロキシを起動させることができる
    ```sh
    $ kubectl proxy
    ```
-->

### 2. クラスタの認証情報を取得

- クラスタの認証情報を取得
    このコマンドにより、作成したクラスタを使用するように `kubectl` が構成される？
    ```sh
    $ gcloud container clusters get-credentials ${CLUSTER_NAME}
    ```

### 3. Deployment を作成する（＝作成したクラスタに、コンテナ化された docker image をデプロイする）

- Deployment を作成する
    ```sh
    $ kubectl create deployment ${CLUSTER_NAME} --image=${IMAGE_NAME}
    ```
    - `${IMAGE_NAME}` : docker コンテナのイメージ名 : ex `gcr.io/${PROJECT_ID}/${IMAGE_NAME}`
        - イメージ名にも `_` は使用できないことに注意

- デプロイされた Deployment の情報を閲覧
    ```sh
    $ kubectl describe deployments
    ```

### 4. Deployment を公開する

- Deployment を公開する
    ```sh
    $ kubectl expose deployment ${CLUSTER_NAME} --type LoadBalancer --port ${PORT} --target-port ${TARGET_PORT}
    ```
    - `${PORT}` : インターネット用公開ポート / ex `80`
    - `${TARGET_PORT}` : アプリケーション用のポート / ex `8080`

### 5. 公開サイトにアクセスして動作確認する

- 実行中の Service を確認
    ```sh
    $ kubectl get service ${CLUSTER_NAME}
    ```
    このコマンドを実行すると、以下のような出力表示される
    ```sh
    NAME             TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE
    sample-cluster   LoadBalancer   10.3.240.39   34.85.65.57   80:30786/TCP   105s
    ```
    `EXTERNAL-IP` のアドレスに `http://${EXTERNAL-IP}/` でアクセスする(今の場合 http://34.85.65.57/ ) ことで、実行中の Service の動作確認をすることが出来る


