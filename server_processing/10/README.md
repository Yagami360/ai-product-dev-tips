# 【GCP】GKE クラスタのノードで GPU を使用可能にする

0. 【事前準備】GPU 割当を確認する
1. GPU 搭載クラスタを作成
2. GPU のノードプールを作成する
3. k8s の DaemonSet での Pod 経由で GPU ドライバーをインストール
    3-1. DaemonSet で使う Docker Image の build と push
    3-2. DaemonSet をデプロイ
4. GPU を使用するように Pod を構成する

- GKE のノードプール<br>
    クラスタ内で同じ構成を持つノードのグループ。

### 1. GPU 搭載クラスタを作成

- GPU 搭載クラスタを作成
    ```sh
    $ gcloud container clusters create ${CLUSTER_NAME} \
        --accelerator type=nvidia-tesla-t4,count=1
    ```
    - `${CLUSTER_NAME}` : 作成するクラスターの名前（`_` は使用できないことに注意）
    - `--accelerator` : 
        - `type` : GPU の種類
            - `nvidia-tesla-k80`, `nvidia-tesla-p100`, `nvidia-tesla-p4`, `nvidia-tesla-v100`, `nvidia-tesla-t4`, `nvidia-tesla-a100`
        - `count`: GPU の数

### 2. GPU のノードプールを作成する
xxx

- GPU 搭載ノードプールを作成する
    ```sh
    $ gcloud container node-pools create ${POOL_NAME} \
        --accelerator type=nvidia-tesla-t4,count=1 \
        --cluster ${CLUSTER_NAME} \
        --num-nodes 3 --min-nodes 0 --max-nodes 3 \
        --enable-autoscaling \
        --machine-type n1-standard-4
    ```
    - `--accelerator` : 
        - `type` : GPU の種類
            - `nvidia-tesla-k80`, `nvidia-tesla-p100`, `nvidia-tesla-p4`, `nvidia-tesla-v100`, `nvidia-tesla-t4`, `nvidia-tesla-a100`
        - `count`: GPU の数
    - `--cluster` : クラスタ名
    - `--num-nodes` : ノード数
    - `--enable-autoscaling` : ノードプールを自動スケーリング
    - `--machine-type` : CPU の種類

### 3. k8s の DaemonSet での Pod 経由で GPU ドライバーをインストール
xxx

### 4. GPU を使用するように Pod を構成する

- taint<br>
    node selector は、特定の Node に特定の Pod をスケジューリングする（＝どこに配置するか決める）ために使用される仕組みであったが、<br>
    taint は、特定の Node に Pod をスケジューリングしないようにするための仕組み<br>
    言い換えると、Pod が不適当な Node にスケジューリングされない（＝配置されない）ようにする仕組み。<br>

GPU ノードプールを作成すると、そのノードプール内のノードには以下の taint が自動的に付与される。
```yml
key: nvidia.com/gpu
effect: NoSchedule      # taint の effect | NoSchedule : taint が許容できなければ node へ schedule させない
```

通常 taint が付与されているノードに対して pod をスケジュールするためには、pod 定義ファイル `deployment.yml` に `toleration` を指定する。<br>
ただし GKE で GPU を利用する場合は toleration ではなく、以下のように pod 定義ファイル `deployment.yml` に `resources` 指定を追加することで GPU ノードプールへのスケジューリングを可能にする。

- `deployment.yml` の中身
```yml
    apiVersion: apps/v1         # Deployment の API バージョン。kubectl api-resources | grep Deployment と kubectl api-versions  | grep apps で確認可能  
    kind: Deployment            # デプロイメント定義ファイルであることを明示
    metadata:
    name: sample-gpu-pod        # 識別名
    spec:
    replicas: 1                 # Pod の数
    selector:
        matchLabels:
        app: sample-gpu-pod     # template:metadata:labels:app と同じ値にする必要がある
    template:
        metadata:
        labels:                 # Pod をクラスタ内で識別のするためのラベル。service.yml で Pod を識別するラベルとして使用される
            app: sample-gpu-pod # 識別名。selector:matchLabels:app と同じ値にする必要がある
        spec:
        containers:             # Pod 内で動作させるコンテナ群の設定
        - image: gcr.io/myproject-292103/sample-image     # Container Registry にアップロードした docker image
            name: sample-container                        # コンテナ名
            ports:
            - containerPort: 80
            name: http-server
        command: ["/bin/bash"]
        resources:              # GPU 使用時には必要
            limits:
            nvidia.com/gpu: 1   # GPU 数
    ```

## 参考サイト
- https://cloud.google.com/kubernetes-engine/docs/how-to/gpus
- https://note.com/oguogura/n/n0ed093c6c51d
