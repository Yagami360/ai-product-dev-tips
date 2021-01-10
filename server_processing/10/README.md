# 【GCP】GKE クラスタのノードで GPU を使用可能にする
GKE クラスタのノードで GPU を使用可能にする手順には、以下のようになる。

0. 【事前準備】GPU 割当を確認する
1. 通常のクラスタを作成
2. GPU のノードプールを作成する
3. DaemonSet での Pod 経由で、ノードプールに GPU ドライバーをインストールする
4. GPU を使用するように Pod を構成し、デプロイする
5. Sevice を公開する
6. 外部アドレスにアクセスして動作確認する

### 1. 通常のクラスタを作成
まず、通常の GPU 非搭載クラスタを作成する。<br>
この時点では、GPU を搭載したクラスタを作成せず、後でこのクラスタに GPU 搭載ノードを追加していく形となる。

- クラスタを作成
    ```sh
    # デフォルトの GKE バージョンでクラスタを作成する場合
    $ gcloud container clusters create ${CLUSTER_NAME} \
        --num-nodes=1
    ```
    ```sh
    # GKE バージョン 1.9 でクラスタを作成する場合
    $ gcloud container clusters create ${CLUSTER_NAME} \
        --num-nodes=1 \
        --cluster-version 1.9.4-gke.1
    ```
    - `${CLUSTER_NAME}` : 作成するクラスターの名前（`_` は使用できないことに注意）
    - `--num-nodes` : ノード数（デフォルトでは３）。GPU割り当ての申請数より大きな数は作成できないことに注意

ここで、Ubuntu のノードイメージを使用する GPU ノードは GKE バージョン 1.11.3 以降でのみ使用可能で、<br>
Container-Optimized OS（COS）のノードイメージを使用する GPU ノードは GKE バージョン 1.9 以降でのみ使用できることに注意。<br>
また、デフォルトでは、Container-Optimized OS のノードイメージが作成されることに注意<br>

各リージョンの GKE バージョンは、以下のコマンドで確認できる。

- GKE バージョンを確認
    ```sh
    $ gcloud container get-server-config --zone ${REGION}
    ```

作成したクラスタのバージョンは、以下のコマンドで確認可能<br>

- クラスタを確認
    ```sh
    $ kubectl get nodes
    NAME                                                  STATUS   ROLES    AGE   VERSION
    gke-sample-gpu-cluster-default-pool-94d5dc5d-wlvl     Ready    <none>   28m   v1.16.15-gke.4901     # クラスターバージョン : v1.16.15-gke.4901
    ```

### 2. GPU のノードプールを作成する

- GKE のノードプール<br>
    クラスタ内で同じ構成を持つノードのグループ。

作成したクラスタに、GPU のノードプールを追加する。

- GPU 搭載ノードプールを作成する
    ```sh
    # ノード数３，CPU : n1-standard-4、GPU : T4 の場合
    $ gcloud container node-pools create ${POOL_NAME} \
        --accelerator type=nvidia-tesla-t4,count=1 \
        --cluster ${CLUSTER_NAME} \
        --num-nodes 3 --min-nodes 3 --max-nodes 3 \
        --enable-autoscaling \
        --machine-type n1-standard-4
    ```
    - https://cloud.google.com/sdk/gcloud/reference/container/node-pools/create
    - `--accelerator` : 
        - `type` : GPU の種類
            - `nvidia-tesla-k80`, `nvidia-tesla-p100`, `nvidia-tesla-p4`, `nvidia-tesla-v100`, `nvidia-tesla-t4`, `nvidia-tesla-a100`
        - `count`: GPU の数
    - `--cluster` : クラスタ名
    - `--num-nodes` : ノード数
    - `--enable-autoscaling` : ノードプールを自動スケーリング
    - `--machine-type` : CPU の種類

作成したノードプールは、以下のコマンドで確認可能

- クラスタを確認
    ```sh
    $ kubectl get nodes
    NAME                                                  STATUS   ROLES    AGE   VERSION
    gke-sample-gpu-cluste-sample-gpu-pool-020622ba-0g7w   Ready    <none>   27m   v1.16.15-gke.4901     # ノードプール
    gke-sample-gpu-cluster-default-pool-94d5dc5d-wlvl     Ready    <none>   28m   v1.16.15-gke.4901     # クラスター
    ```

ノードプールの削除は、以下のコマンドで可能

- ノードプールの削除
    ```sh
    $ gcloud container node-pools delete ${POOL_NAME} --cluster ${CLUSTER_NAME}
    ```

### 3. DaemonSet での Pod 経由で、ノードプールに GPU ドライバーをインストール

- DaemonSet<br>
    ReplicaSet は、クラスタ内に事前に指定した数の Pod が常に起動している状態を保持するための機能であったが、各ノードの Pod 数が常に同じ数で配置されることを保証するものではない。<br>
    一方 DaemonSet は、クラスタ内の全ノードに１つの Pod づつ配置されるようにした ReplicaSet の一種になっている。用途としては、全 Node 上で必ず動作している必要のあるプロセスのために利用されることが多い。<br>
    
GKE クラスタのノードで GPU を使用可能にする場合には、NVIDIA の GPU ドライバを DaemonSet 経由でインストールする。<br>
これにより、オートスケーリングによって新しく GPU ノードが作成されたとしても、そのノードに GPU ドライバが自動的にインストールされる。

- DaemonSet をデプロイ（ノードプールの OS が Container-Optimized OS の場合）
    デフォルトでは、ノードプールの OS が Container-Optimized OS になるので、こちらのコマンドを使用すること
    ```sh
    $ kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
    ```
- DaemonSet をデプロイ（ノードプールの OS が Ubuntu の場合）
    ```sh
    $ kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/ubuntu/daemonset-preloaded.yaml
    ```

GPU ドライバーが正しくインストールされたかは、以下のコマンドで確認可能

- kube-system namespace を確認
    ```sh
    $ kubectl get pods -n=kube-system
    ```
    ```sh
    # GPU ドライバーインストール失敗時
    NAME                                                             READY   STATUS                  RESTARTS   AGE
    event-exporter-gke-77cccd97c6-gq4cc                              2/2     Running                 0          7m50s
    fluentd-gke-cb9n7                                                2/2     Running                 0          3m58s
    fluentd-gke-llbsh                                                2/2     Running                 0          6m3s
    fluentd-gke-scaler-54796dcbf7-lb8rg                              1/1     Running                 0          7m47s
    gke-metrics-agent-4xlf4                                          1/1     Running                 0          7m33s
    gke-metrics-agent-z8c86                                          1/1     Running                 0          3m58s
    kube-dns-7bb4975665-4d6b7                                        4/4     Running                 0          7m50s
    kube-dns-7bb4975665-96lnr                                        4/4     Running                 0          3m55s
    kube-dns-autoscaler-645f7d66cf-pqqf4                             1/1     Running                 0          7m45s
    kube-proxy-gke-sample-gpu-cluste-sample-gpu-pool-e94109bc-g120   1/1     Running                 0          3m58s
    kube-proxy-gke-sample-gpu-cluster-default-pool-659f2df2-l5nd     1/1     Running                 0          7m33s
    l7-default-backend-678889f899-7572h                              1/1     Running                 0          7m50s
    metrics-server-v0.3.6-64655c969-k69l4                            2/2     Running                 0          7m10s
    nvidia-driver-installer-qb7lt                                    0/1     Init:CrashLoopBackOff   3          78s     # GPUドライバのインストールに失敗している
    nvidia-gpu-device-plugin-dqkwq                                   1/1     Running                 0          3m58s
    prometheus-to-sd-4q6qj                                           1/1     Running                 0          7m33s
    prometheus-to-sd-np7hs                                           1/1     Running                 0          3m58s
    stackdriver-metadata-agent-cluster-level-655fb4655f-5v9pn        2/2     Running                 1          6m48s
    ```
    ```sh
    # GPU ドライバーインストール成功時
    NAME                                                             READY   STATUS    RESTARTS   AGE
    event-exporter-gke-77cccd97c6-qvvr6                              2/2     Running   0          8m3s
    fluentd-gke-jchdm                                                2/2     Running   0          85s
    fluentd-gke-scaler-54796dcbf7-gqss7                              1/1     Running   0          8m1s
    fluentd-gke-xdgvf                                                2/2     Running   5          6m36s
    gke-metrics-agent-kzwcc                                          1/1     Running   0          6m36s
    gke-metrics-agent-sz6f5                                          1/1     Running   0          7m48s
    kube-dns-7bb4975665-6w76q                                        4/4     Running   0          6m28s
    kube-dns-7bb4975665-rdhb6                                        4/4     Running   0          8m3s
    kube-dns-autoscaler-645f7d66cf-5bcq6                             1/1     Running   0          7m59s
    kube-proxy-gke-sample-gpu-cluste-sample-gpu-pool-667dc9b1-fx8d   1/1     Running   0          6m36s
    kube-proxy-gke-sample-gpu-cluster-default-pool-a3021f17-nk9s     1/1     Running   0          7m48s
    l7-default-backend-678889f899-p6x9v                              1/1     Running   0          8m4s
    metrics-server-v0.3.6-64655c969-59sv8                            2/2     Running   4          7m22s
    nvidia-driver-installer-8k7hh                                    1/1     Running   0          85s
    nvidia-gpu-device-plugin-zgplc                                   1/1     Running   0          6m36s
    prometheus-to-sd-kh4vv                                           1/1     Running   0          6m36s
    prometheus-to-sd-rmqjk                                           1/1     Running   0          7m48s
    stackdriver-metadata-agent-cluster-level-655fb4655f-qtxc5        2/2     Running   5          6m59s
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
    apiVersion: v1                  # API バージョン  
    kind: Pod                       # Podであることを明示
    metadata:
        name: sample-gpu-pod        # 識別名
      labels:
        app: sample-gpu-pod         # Pod をクラスタ内で識別のするためのラベル。service.yml で Pod を識別するラベルとして使用される
    spec:
        restartPolicy: OnFailure    # 失敗時のみコンテナを再起動。Pod や Job 作成時に指定
        containers:                 # Pod 内で動作させるコンテナ群の設定
        - image: gcr.io/myproject-292103/sample-image     # Container Registry にアップロードした docker image
            name: sample-container                        # コンテナ名
            ports:
            - containerPort: 80                           # 通信ポート番号
            name: http-server
        #command: ["/bin/bash"]     # 起動後一度だけ実行したいコマンドを指定。指定するとコマンド完了後 READY 0/1 となることに注意
        resources:                  # GPU 使用時には必要
            limits:
            nvidia.com/gpu: 1       # GPU 数
    ```
    - `restartPolicy` : コンテナが失敗した際の再起動のポリシー
        - `Always` : Deployment 作成時に指定（デフォルト値）。Pod や Job 作成時には指定不可
        - `OnFailure` : 失敗時のみコンテナを再起動。Pod や Job 作成時に指定
        - `Never` : コンテナを再起動しない。Pod や Job 作成時に指定

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
以下のコマンドで Service を公開することで、Service とロードバランサーが作成され、外部から指定したIPアドレスにアクセスできるようになる。

- yaml ファイルありで Service を公開する
    ```sh
    $ kubectl apply -f ${サービス定義ファイル（.yml）}
    ```
    ```sh
    # 使用例
    $ kubectl apply -f k8s/service.yml
    ```

以下のコマンドで、作成した Pod のコンテナにアクセスして、`nvidia-smi` コマンドが実行可能であれば、正しく GPU ドライバーがインストールできている。

- Pod のコンテナにアクセスして、nvidia-smi コマンド実行
    ```sh
    $ kubectl exec -it ${POD_NAME} /bin/bash
    $ nvidia-smi
    ```
    - `${POD_NAME}` : Pod 名。`kubectl get pods` で確認可能<br>
    - ※ node のインスタンスではなく、master のインスタンスにアクセスしている状態になることに注意

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
- https://thenewstack.io/getting-started-with-gpus-in-google-kubernetes-engine/