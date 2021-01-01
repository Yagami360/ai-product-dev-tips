# 【GCP】GKE [Google Kubernetes Engine] の基本事項

## ■ Kubernetes (k8s) と GKE の基本事項

### ◎ Kubernetes (k8s)
Kubernetes（クーベネティス）は、コンテナの運用管理と自動化（＝コンテナオーケストレーション）を行うシステムで、複数サーバーで分散環境されたシステムをあたかも１台のコンピューターのように扱えるようになる。<br>

具体的には、以下のような機能を持つ

- 複数サーバーでのコンテナ管理
- コンテナのスケジューリング
- オートスケーリング、ロードバランシング（負荷分散）
- コンテナの死活監視
- 障害時のセルフヒーリング
- ログの管理

多数のコンテナから構成され、それらを適切にスケーリングする必要があるシステムにおいて、Kubernetes を導入することで、システムの管理が用意になるというメリットがある。

<img src="https://user-images.githubusercontent.com/25688193/103432871-467f0900-4c2a-11eb-982b-d2d82fb29056.png" width=600>

上図は Kubernetes のアーキテクチャを示した図である。<br>
Kubernetes は、以下のようなコンポーネントから構成される

- Kubernetes クラスタ<br>
    Kubernetes では、後述の master サーバー と複数の Node 全体で１つのクラスタという処理単位で扱う。

- master サーバー<br>
    クラスタ内のコンテナを操作するためのサーバー。<br>
    複数のサーバーから構築されている負荷分散システムでは、各々のサーバー（Node）に対してそのサーバー内のコンテナにアスセスする方法ではうまく連携が取れなくなるので、複数の Node を管理している master サーバーを介して、クラスタ内の各コンテナを操作できるようになっている。

- Node<br>
    Dockerが動くサーバーのこと。

- Pod<br>
    コンテナを配置する入れ物で１つ以上のコンテナを持つ。Kubernetes ではこの単位でスケーリングされ、アプリケーションのデプロイ単位になる。そして、コンテナの起動・停止などの処理はこの Pod 単位で行われる。<br>Pod 単位で管理するので、役割の異なるコンテナ（データベースコンテナと Web フロントコンテナなど）を１つの Pod 内に格納するのは一般的に NG となる。<br>
    Pod の設定は yaml ファイルで記述する。

- ReplicaSet<br>
    クラスタ内に、事前に指定した数の Pod が常に起動している状態を保持するための機能。障害などで Pod が停止してしまった場合、その Pod を削除し、Pod を新規に作成することで常に必要な数の Pod が起動した状態を保持する。（いわゆるオートスケーリングを行っている機能）

- Deployments<br>
    <img src="https://user-images.githubusercontent.com/25688193/103432768-b7bdbc80-4c28-11eb-9b5f-33c3330c4b33.png" width=350><br>
    Pod（コンテナ）と ReplicaSet をまとめて管理し、それらの履歴を管理する機能。Deployments は ReplicaSet のテンプレートを持ち、そのテンプレートに従って ReplicaSet と Pod を作成する。これにより、Pod 内コンテナの docker image を更新したい場合に、システムを停止することなく更新できるようになる。また履歴も管理しているので、Pod 内コンテナの docker image を古いバージョンに更新することもできる。

- Service（ネットワーク管理）<br>
    クラスタ内の各 Pod に対して、アクセス可能な IP アドレスを付与し、外部からアクセスできるようにしたもの。Service の設定は yaml ファイルで記述する。

- DaemonSet<br>
    xxx

### ◎ GKE の基本事項
GKE [Google Kubernetes Engine] は、Google が提供している Kubernetes (k8s) のマネージドサービスで、Kubernetes を GUI でより手軽に扱ったり、既存の GCP サービスとの連携などを行うことができる。<br>
GKE を利用して Kubernetes クラスタを構築する際には、以下の GCP サービスを利用することが多い

- Google Container Builder<br>
    Dockerfile を元に docker image を作成する作業を、ローカルPCやサーバー上で行うのでなく、GCP 上で行うことのできるサービス。作成した docker image は、Google Conatainer Registry に自動的にアップロードされる。<br>
- Google Conatainer Registry
    docker image を GCP プロジェクト内で管理できるストレージサービス。docker image のアップロードとダウンロードができる。

## ■ GKE を利用した Kubernetes クラスターの構築手順

0. 【事前準備】作成した api コードの docker image を作成し、GCP の Container Registry にアップロード
1. クラスタを作成
1. Deployment を作成する
1. Service を公開する
1. 公開サイトにアクセスして動作確認する


- xxx
    1. yaml ファイルなしで Pod と Deployment を作成する場合
    1. yaml ファイルありで Pod と Deployment を作成する場合

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
        - ノートは GCP での VM インスタンスに相当

<!--
- Kubernetes のローカルプロキシを起動
    上記コマンドでクラスターを作成した時点で、既にKubernetesも起動しているので、以下のコマンドでローカルプロキシを起動させることができる
    ```sh
    $ kubectl proxy
    ```
-->

### 1.1. クラスタの認証情報を取得

- クラスタの認証情報を取得
    このコマンドにより、作成したクラスタを使用するように `kubectl` が構成される？
    ```sh
    $ gcloud container clusters get-credentials ${CLUSTER_NAME}
    ```

### 2. Deployment を作成する
作成したクラスタの各 Node に、docker image のコンテナを Pod 単位でデプロイする。

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

### 4. Service を公開する
Service を公開指定ない状態では、Node 内でコンテナが動いているだけであり、外部からアクセスすることができない状態になっている。<br>
以下のコマンドで Deployment を公開することで、Service とロードバランサーが作成され、外部から指定したIPアドレスにアクセスできるようになる。

- Service を公開する
    ```sh
    $ kubectl expose deployment ${CLUSTER_NAME} --type LoadBalancer --port ${PORT} --target-port ${TARGET_PORT}
    ```
    - `${PORT}` : インターネット用公開ポート / ex `80`
    - `${TARGET_PORT}` : アプリケーション用のポート / ex `8080`
    - `--type` : 
        - LoadBalancer 指定時：Service の IPアドレス＋ポート番号にアクセスすると、複数の Pod でのレイヤー４レベルの負荷分散を行う

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


### その他コマンド

作成した Pod のコンテナ内部にアクセスしたい場合は、以下のコマンドでアクセスできる

```sh
$ kubectl exec -it ${Pod名} /bin/bash
```
- ※ node のインスタンスではなく、master のインスタンスにアクセスしている状態になることに注意


Pod 名は、以下のコマンドで確認可能

```
$ kubectl get pod
```


## ■ 参考サイト
- https://cloud.google.com/kubernetes-engine/docs/quickstart#dockerfile
- https://qiita.com/ntoreg/items/74aa6de2f8f29b4a3b79
- https://www.topgate.co.jp/gcp07-how-to-start-docker-image-gke
- https://www.kagoya.jp/howto/rentalserver/kubernetes/
