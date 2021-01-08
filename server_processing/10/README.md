# 【GCP】GKE クラスタのノードで GPU を使用可能にする

0. 【事前準備】GPU 割当を確認する
1. GPU 搭載クラスタを作成
2. GPU のノードプールを作成する
3. k8s の DaemonSet での Pod 経由で GPU ドライバーをインストール
4. GPU を使用するように Pod を構成し、デプロイする
5. Sevice を公開する
6. 外部アドレスにアクセスして動作確認する

### 1. GPU 搭載クラスタを作成

- GPU 搭載クラスタを作成
    ```sh
    $ gcloud container clusters create ${CLUSTER_NAME} \
        --num-nodes=1 \
        --accelerator type=nvidia-tesla-t4,count=1
    ```
    - `${CLUSTER_NAME}` : 作成するクラスターの名前（`_` は使用できないことに注意）
    - `--num-nodes` : ノード数（デフォルトでは３）。GPU割り当ての申請数より大きな数は作成できないことに注意
    - `--accelerator` : 
        - `type` : GPU の種類
            - `nvidia-tesla-k80`, `nvidia-tesla-p100`, `nvidia-tesla-p4`, `nvidia-tesla-v100`, `nvidia-tesla-t4`, `nvidia-tesla-a100`
        - `count`: GPU の数

### 2. GPU のノードプールを作成する

- GKE のノードプール<br>
    クラスタ内で同じ構成を持つノードのグループ。

作成した GPU 搭載クラスタに、GPU のノードプールを追加する。

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


作成したノードプールは、作成した GKE クラスタの GUI 画面の「ノード」タブから確認可能<br>
<img src="https://user-images.githubusercontent.com/25688193/104014131-e4a83b80-51f5-11eb-9bc1-c1820879062b.png" width="500">

### 3. k8s の DaemonSet での Pod 経由で GPU ドライバーをインストール

- DaemonSet<br>
    ReplicaSet は、クラスタ内に事前に指定した数の Pod が常に起動している状態を保持するための機能であったが、各ノードの Pod 数が常に同じ数で配置されることを保証するものではない。<br>
    一方 DaemonSet は、クラスタ内の全ノードに１つの Pod づつ配置されるようにした ReplicaSet の一種になっている。用途としては、全 Node 上で必ず動作している必要のあるプロセスのために利用されることが多い。<br>
    
    
GKE クラスタのノードで GPU を使用可能にする場合には、NVIDIA の GPU ドライバを DaemonSet 経由でインストールする。<br>
これにより、オートスケーリングによって新しく GPU ノードが作成されたとしても、そのノードに GPU ドライバが自動的にインストールされる。

- DaemonSet をデプロイ（＝yaml ファイルありで Pod と Deployment を作成するときと同じコマンド）
    ```sh
    $ kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/ubuntu/daemonset-preloaded.yaml
    ```

### 4. GPU を使用するように Pod を構成し、デプロイする

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
    apiVersion: v1       # API バージョン  
    kind: Pod            # Podであることを明示
    metadata:
        name: sample-gpu-pod        # 識別名
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

デプロイメント定義ファイル `deployment.yml` を作成後、以下のコマンドで yml ファイルに従った Pod を作成できる。（＝Pod をデプロイする）<br>
※ Deployment は作成しないことに注意

- yaml ファイルありで Pod を作成（＝Pod をデプロイする）
    ```sh
    $ kubectl apply -f ${デプロイメント定義ファイル（.yml）}
    ```
    ```sh
    # 使用例
    $ kubectl apply -f k8s/deployment.yml
    ```

### 5. Service を公開する
Service を公開指定ない状態では、Node 内でコンテナが動いているだけであり、外部からアクセスすることができない状態になっている。<br>
以下のコマンドで Deployment を公開することで、Service とロードバランサーが作成され、外部から指定したIPアドレスにアクセスできるようになる。

- yaml ファイルありで Service を公開する
    ```sh
    $ kubectl apply -f ${サービス定義ファイル（.yml）}
    ```
    ```sh
    # 使用例
    $ kubectl apply -f k8s/service.yml
    ```

### 6. 外部アドレスにアクセスして動作確認する
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

## 参考サイト
- https://cloud.google.com/kubernetes-engine/docs/how-to/gpus
- https://note.com/oguogura/n/n0ed093c6c51d
