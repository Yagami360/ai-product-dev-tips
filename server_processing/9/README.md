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

- DaemonSet<br>
    ReplicaSet は、クラスタ内に事前に指定した数の Pod が常に起動している状態を保持するための機能であったが、各ノードの Pod 数が常に同じ数で配置されることを保証するものではない。<br>
    一方 DaemonSet は、クラスタ内の全ノードに１つの Pod づつ配置されるようにした ReplicaSet の一種になっている。用途としては、全 Node 上で必ず動作している必要のあるプロセスのために利用されることが多い。<br>
    例えば、GKE クラスタのノードで GPU を使用可能にする場合には、NVIDIA のデバイスドライバを DaemonSet 経由でインストールする。これによってオートスケーリング機能の良さを殺さずにデバイスドライバのインストールを実現できる。

- Deployments<br>
    <img src="https://user-images.githubusercontent.com/25688193/103432768-b7bdbc80-4c28-11eb-9b5f-33c3330c4b33.png" width=350><br>
    Pod（コンテナ）と ReplicaSet をまとめて管理し、それらの履歴を管理する機能。Deployments は ReplicaSet のテンプレートを持ち、そのテンプレートに従って ReplicaSet と Pod を作成する。これにより、Pod 内コンテナの docker image を更新したい場合に、システムを停止することなく更新できるようになる。また履歴も管理しているので、Pod 内コンテナの docker image を古いバージョンに更新することもできる。

- Job<br>
    1つ以上の Pod を作成し、指定された数の Pod が正常に終了するのを保証するための仕組み。<br>

- CronJob<br>
    xxx

- Service（ネットワーク管理）<br>
    クラスタ内の各 Pod に対して、アクセス可能な IP アドレスを付与し、外部からアクセスできるようにしたもの。Service の設定は yaml ファイルで記述する。


### ◎ GKE の基本事項
GKE [Google Kubernetes Engine] は、Google が提供している Kubernetes (k8s) のマネージドサービスで、Kubernetes を GUI でより手軽に扱ったり、既存の GCP サービスとの連携などを行うことができる。<br>
GKE を利用して Kubernetes クラスタを構築する際には、以下の GCP サービスを利用することが多い

- Google Container Builder<br>
    Dockerfile を元に docker image を作成する作業を、ローカルPCやサーバー上で行うのでなく、GCP 上で行うことのできるサービス。作成した docker image は、Google Conatainer Registry に自動的にアップロードされる。<br>
- Google Conatainer Registry
    docker image を GCP プロジェクト内で管理できるストレージサービス。docker image のアップロードとダウンロードができる。

## ■ GKE を利用した Kubernetes クラスターの構築手順

0. 【事前準備】作成した api コードの docker image を作成し、GCP の Container Registry にアップロード<br>
1. クラスタを作成<br>
2. Deployment を作成する<br>
    2-1. yaml ファイルなしで Pod と Deployment を作成する場合<br>
    2-2. yaml ファイルありで Pod と Deployment を作成する場合<br>
3. Service を公開する<br>
    3-1. yaml ファイルなしで Service を作成する場合<br>
    3-1. yaml ファイルありで Service を作成する場合<br>
4. 外部アドレスにアクセスして動作確認する<br>
    4-1. 公開外部アドレスの URL にアドレスして動作確認する<br>
    4-2. 公開外部アドレスにリクエスト処理して、レスポンスを受け取る<br>

### 0. 【事前準備】作成した api コードの docker image を作成し、GCP の Container Registry にアップロード

- 作成済みの docker image を GCP の Container Registry にアップロード
    ```sh
    # docker image に TAG をつける
    # TAG 名 : gcr.io/${PROJECT_ID}/${IMAGE_NAME}
    $ docker tag ${IMAGE_NAME} gcr.io/${PROJECT_ID}/${IMAGE_NAME}

    # Container Registry にアップロード（TAGを使用）
    $ docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}
    ```
    - `${PROJECT_ID}` : GCP プロジェクト名
    - `${IMAGE_NAME}` : docker image 名
        - イメージ名にも `_` は使用できないことに注意

- docker image を作成し、GCP の Container Registry にアップロード
    ソースコードと Dockerfile が格納されているディレクトリから次のコマンドを実行。
    ```sh
    $ gcloud builds submit --tag gcr.io/${PROJECT_ID}/${IMAGE_NAME}
    ```

- `cloudbuild.yml` の設定情報を元に docker image を作成し、GCP の Container Registry にアップロード
    ソースコードと Dockerfile が格納されているディレクトリから次のコマンドを実行。
    ```sh
    $ gcloud builds submit --config ${cloudbuildの設定ファイル名（.yml）}
    ```
    - `cloudbuild.yml` ファイルの中身
        ```yml
        steps:
        - name: 'gcr.io/cloud-builders/docker'  # docker コマンドを実行するには必要
            args: ['build', '-t', 'gcr.io/myproject-292103/sample-image', './api']  # ./api に格納されている dockerfile を元に、docker image を作成
        images: ['gcr.io/myproject-292103/sample-image']
        ```

※ Dockerfile 内では、`EXPOSE` 命令で使用するコンテナ通信ポートの設定をする必要があることに注意

### 1. クラスタを作成

#### ☆ GUI 使用時
[GKE の GUI 画面上](https://console.cloud.google.com/kubernetes/list?project=myproject-292103&folder&organizationId) から作成できる

#### ☆ GUI 非使用時

- クラスタを作成
    ```sh
    $ gcloud container clusters create ${CLUSTER_NAME} --num-nodes=3
    ```
    - `${CLUSTER_NAME}` : 作成するクラスターの名前（`_` は使用できないことに注意）
    - `--num-nodes` : ノード数（デフォルトでは３）
        - ノートは GCP での VM インスタンスに相当

<!--
- Kubernetes のローカルプロキシを起動
    上記コマンドでクラスターを作成した時点で、既にKubernetesも起動しているので、以下のコマンドでローカルプロキシを起動させることができる
    ```sh
    $ kubectl proxy
    ```
-->

作成したクラスタの各ノードは、以下のコマンドで確認できる

- クラスタのノードを確認
    ```sh
    $ kubectl get nodes
    ```

### 1.1. クラスタの認証情報を取得

- クラスタの認証情報を取得
    このコマンドにより、作成したクラスタを使用するように `kubectl` が構成される？
    ```sh
    $ gcloud container clusters get-credentials ${CLUSTER_NAME}
    ```

### 2. Deployment を作成する
作成したクラスタの各 Node に、docker image のコンテナを Pod 単位でデプロイする。

### 2-1. yaml ファイルなしで Pod と Deployment を作成する場合
`kubectl run`, `kubectl create`, `kubectl expose` コマンドを使用することで、yaml ファイルなしに Pod, Deployment, Service を手軽に作成できる。

- yaml ファイルなしに Pod と Deployment を作成
    ```sh
    $ kubectl run ${POD_NAME} --image=${IMAGE_NAME}
    ```
    ```sh
    # 例）nginx を起動する場合
    $ kubectl run nginx --image=nginx:1.11.3
    ```

- yaml ファイルなしに Pod と Deployment を作成
    ```sh
    $ kubectl create deployment ${POD_NAME} --image=${IMAGE_NAME}
    ```
    - `${IMAGE_NAME}` : docker コンテナのイメージ名 : ex `gcr.io/${PROJECT_ID}/${IMAGE_NAME}`
        - イメージ名にも `_` は使用できないことに注意

作成した Pod や Deployment は、以下の `kubectl get`, `kubectl describe` コマンドで確認可能

- Pod の確認
    ```sh
    $ kubectl get pods
    NAME                         READY   STATUS    RESTARTS   AGE
    nginx-pod-7d8dc9d9f9-7p8mg   1/1     Running   0          13s
    nginx-pod-7d8dc9d9f9-sgl5g   1/1     Running   0          13s
    nginx-pod-7d8dc9d9f9-tqqxj   1/1     Running   0          13s
    ```

- Pod の確認（詳細）
    ```sh
    $ kubectl describe pods
    ```

- Deployment の確認
    ```sh
    $ kubectl get deployments
    NAME        READY   UP-TO-DATE   AVAILABLE   AGE
    nginx-pod   3/3     3            3           40s
    ```

- Deployment の確認（詳細）
    ```sh
    $ kubectl describe deployments
    ```

作成した Pod や Deployment は、以下のコマンドで削除可能

- Pod と Deployment を削除
    ```sh
    $ kubectl delete deployment ${POD_NAME}
    ```

### 2-2. yaml ファイルありで Pod と Deployment を作成する場合

この場合まず、Pod の設定をデプロイメント定義ファイル `deployment.yml`（ファイル名は任意）に記述する。

- `deployment.yml` の中身
    ```yml
    apiVersion: apps/v1         # Deployment の API バージョン。kubectl api-resources | grep Deployment と kubectl api-versions  | grep apps で確認可能  
    kind: Deployment            # デプロイメント定義ファイルであることを明示
    metadata:
    name: sample-pod          # Pod の名前
    spec:
    replicas: 3               # Pod の数
    selector:
        matchLabels:
        app: sample-pod       # template:metadata:labels:app と同じ値にする必要がある
    template:                 # Pod のテンプレート。このテンプレートをもとに ReplicaSet がレプリカ数の Pod を作成する
        metadata:
        labels:               # Pod をクラスタ内で識別のするためのラベル。service.yml で Pod を識別するラベルとして使用される
            app: sample-pod   # ↑
        spec:
        containers:               # Pod 内で動作させるコンテナ群の設定
        - image: gcr.io/myproject-292103/sample-image     # Container Registry にアップロードした docker image
            name: sample-container                          # コンテナ名
            env:                    # ConfigMap と Secret を Pod で利用するための設定情報（ConfigMap と Secret を利用しない場合は、これらの定義は不要）
            - name: PROJECT_ID                              # ConfigMap で定義した project.id
            valueFrom:
                configMapKeyRef:
                name: projectid
                key: project.id
            - name: SECRET_ID                               # Secret で定義した apikey の id
            valueFrom:
                secretKeyRef:
                name: apikey
                key: id
            - name: SECRET_KEY                              # Secret で定義した apikey の key
            valueFrom:
                secretKeyRef:
                name: apikey
                key: key
            ports:
            - containerPort: 80    # コンテナの通信ポート番号
            name: http-server
    ```

デプロイメント定義ファイル `deployment.yml` を作成後、以下のコマンドで yml ファイルに従った Pod と Deployment を作成できる。

- yaml ファイルありで Pod と Deployment を作成
    ```sh
    $ kubectl apply -f ${デプロイメント定義ファイル（.yml）}
    ```
    ```sh
    # 使用例
    $ kubectl apply -f k8s/deployment.yml
    ```

### 3. Service を公開する
Service を公開指定ない状態では、Node 内でコンテナが動いているだけであり、外部からアクセスすることができない状態になっている。<br>
以下のコマンドで Deployment を公開することで、Service とロードバランサーが作成され、外部から指定したIPアドレスにアクセスできるようになる。

#### 3-1. yaml ファイルなしで Service を作成する場合

- yaml ファイルなしで Service を公開する
    ```sh
    $ kubectl expose deployment ${POD_NAME} --type LoadBalancer --port ${PORT} --target-port ${TARGET_PORT}
    ```
    - `${PORT}` : インターネット用公開ポート / ex `80`
    - `${TARGET_PORT}` : アプリケーション用のポート / ex `80`
    - `--type` : 
        - LoadBalancer 指定時：Service の IPアドレス＋ポート番号にアクセスすると、複数の Pod でのレイヤー４レベルの負荷分散を行う

#### 3-2. yaml ファイルありで Service を作成する場合
この場合まず、Service の設定をサービス定義ファイル `service.yml`（ファイル名は任意）に記述する。

- `service.yml` の中身
    ```yml
    apiVersion: v1
    kind: Service           # サービス定義ファイルであることを明示
    metadata:
    name: sample-server     # サービス名
    spec:
    type: LoadBalancer      # ロードバランサーを指定。
    ports:
        - port: 80          # インターネット用公開ポート
        targetPort: 80      # アプリケーション用のポート
        protocol: TCP
    selector:               # リクエストをうけるコンテナの設定
        app: sample-pod     # デプロイメント定義ファイルで定義した Pod の識別名。この場合 app:sample-pod のラベルがつけられた Pod を通信先とする
    ```

- yaml ファイルありで Service を公開する
    ```sh
    $ kubectl apply -f ${サービス定義ファイル（.yml）}
    ```
    ```sh
    # 使用例
    $ kubectl apply -f k8s/service.yml
    ```

作成したサービスは、以下のコマンドで確認できる

- サービスの確認
    ```sh
    $ kubectl get service
    NAME           TYPE           CLUSTER-IP    EXTERNAL-IP    PORT(S)        AGE
    kubernetes     ClusterIP      10.3.240.1    <none>         443/TCP        111m
    nginx-server   LoadBalancer   10.3.252.30   34.84.63.179   80:31088/TCP   76s
    ```
    ```sh
    $ kubectl get service ${SERVICE_NAME}
    ```

- サービスの確認（詳細）
    ```sh
    $ kubectl describe service ${SERVICE_NAME}
    ```

作成した Service は、以下のコマンドで削除可能

- Service を削除
    ```sh
    $ kubectl delete service ${SERVICE_NAME}
    ```

### 4. 外部アドレスにアクセスして動作確認する

#### 4-1. 公開外部アドレスの URL にアドレスして動作確認する
`kubectl get service` で表示される `EXTERNAL-IP` のアドレスに `http://${EXTERNAL-IP}:${PORT}` でアクセスすることで、実行中の Service の動作確認をすることが出来る。

- 公開サイトへのアスセス
    ```sh
    $ curl http://${EXTERNAL_IP}:${PORT}
    ```
    - ${EXTERNAL_IP} : `kubectl get service` で表示される `EXTERNAL-IP` のアドレス。<br>
        以下のコマンドでも取得できる
        ```sh
        $ EXTERNAL_IP=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`
        ```

#### 4-2. 公開外部アドレスにリクエスト処理して、レスポンスを受け取る
作成したクラスタのコンテナの docker image が image 化された API コード（Flask を用いたコードなど）である場合は、`kubectl get service` で表示される `EXTERNAL-IP` のアドレスに、リクエストメッセージを送信することで、作成したクラスタからレスポンスメッセージを受け取ることができる。（処理内容は docker image 化されたコード内容による）

## ■ その他便利コマンド

- 作成した Pod のコンテナログを確認する
    デバッグ用途などで、作成した Pod のコンテナログを確認したい場合は、以下のコマンドで確認できる
    ```sh
    kubectl logs ${POD_NAME}
    ```
    - `${POD_NAME}` : Pod 名。`kubectl get pods` で確認可能<br>
        Pod 数が１個の場合は、以下のコマンドでも取得できる
        ```sh
        $ POD_NAME=`kubectl get pods | awk '{print $1}' | sed -n 2p`
        ```

- 作成した Pod のコンテナ内部にアクセス<br>
    デバッグ用途などで、作成した Pod のコンテナ内部にアクセスしたい場合は、以下のコマンドでアクセスできる
    ```sh
    $ kubectl exec -it ${POD_NAME} /bin/bash
    ```
    - `${POD_NAME}` : Pod 名。`kubectl get pods` で確認可能<br>
    - ※ node のインスタンスではなく、master のインスタンスにアクセスしている状態になることに注意

## ■ 参考サイト
- https://cloud.google.com/kubernetes-engine/docs/quickstart#dockerfile
- https://qiita.com/ntoreg/items/74aa6de2f8f29b4a3b79
- https://www.topgate.co.jp/gcp07-how-to-start-docker-image-gke
- https://www.kagoya.jp/howto/rentalserver/kubernetes/
