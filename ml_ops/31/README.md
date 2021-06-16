# 【GKE】GKE でのオートスケールの基礎事項

<img src="https://user-images.githubusercontent.com/25688193/121995092-60c83000-cde1-11eb-8b25-ecf1735b3fbe.png" width="600"><br>

GKE でのオートスケールには、以下の５種類が存在する
1. 水平 Pod オートスケール [HPA : Horizontal Pod Autoscaling]<br>
    Pod 数をスケーリングさせるオートスケール
1. 垂直 Pod オートスケール [VPA]<br>
    １つの Pod のリソース量（＝垂直方向）をスケーリングするオートスケール
1. 多次元 Pod オートスケール [MPA]<br>
    水平 Pod オートスケールと垂直 Pod オートスケールを同時に実現するオートスケール<br>
1. クラスタ・オートスケール [CA : Cluster Autoscaler]<br>
   ノードプール内のノード数（=GCE サーバー数）をスケーリングさせるオートスケール
1. ノード自動プロビジョニング [NAP]<br>
    ノードプールをスケーリングさせるオートスケール

## ■ 水平 Pod オートスケール (HPA)
水平 Pod オートスケールは、（ノードではなく）Pod 数をスケーリングさせるオートスケールになっている<br>

> k8s 自体に実装されている機能で、GKE の独自機能ではないことに注意。そのため、`kubectl` コマンドでオートスケールの設定をで行う

- 設定方法１：`HorizontalPodAutoscaler` で指定<br>
    ```yaml
    apiVersion: autoscaling/v2beta1
    kind: HorizontalPodAutoscaler
    metadata:
    name: php-hpa
    namespace: default
    spec:
    scaleTargetRef: # ここでautoscale対象となる`scaled resource object`を指定
        apiVersion: apps/v1
        kind: Deployment
        name: php-deploy
    minReplicas: 1 # 最小レプリカ数
    maxReplicas: 5 # 最大レプリカ数
    metrics:
    - type: Resource
        resource:
        name: cpu
        targetAverageUtilization: 50 # CPU使用率が常に50%になるように指定
    ```

    ```sh
    $ kubectl apply -f hpa-test.yaml
    ```

- 設定方法２：`kubectl autoscale` コマンドで指定<br>
    作成した Pod に対して `kubectl autoscale` コマンドでオートスケールの設定を行う
    ```sh
    kubectl autoscale deployment sample-pod --max 5 --min 1 --cpu-percent 70
    ```

- オートスケールのトリガー
    Pod の負荷 (= 指標値) が指定した水準に合致するように、稼働する Pod の数が増減されます。<br>
    GKE では、CPU やメモリのような基本的な指標だけではなく、Cloud Monitoring の指標 に基づいた判定もできる。

## ■ 垂直 Pod オートスケール [VPA]
垂直 Pod オートスケールは、１つの Pod のリソース量（＝垂直方向）をスケーリングするオートスケールになっている。

## ■多次元 Pod オートスケール
水平 Pod オートスケールと垂直 Pod オートスケールを同時に実現するオートスケール<br>
GKE の独自機能で、v1.19.4-gke.1700 から利用可能になっている

## ■ クラスタ・オートスケール [CA : Cluster Autoscaler] / 自動スケーリングの有効化
クラスタ・オートスケールは、（Pod ではなく）ノードプール内のノード数（=GCE サーバー数）をスケーリングさせるオートスケールになっている<br>
> クラスタ自体をオートスケールするわけではないことに注意

- 設定方法<br>
    `gcloud container clusters create` コマンド実行時に `--min-nodes`, `--max-nodes`, `--enable-autoscaling` でオートスケールするノードの最小数と最大数を指定することで設定できる。
    ```sh
    $ gcloud container clusters create sample-cluster \
        --num-nodes=3 --min-nodes=1 --max-nodes=3 \
        --machine-type=f1-micro \
        --enable-autoscaling
    ```

    > GKE コンソールを使用する場合は、クラスタ作成時の「自動スケーリングの有効化」で指定できる

- リソースの指定方法<br>
    `gcloud container clusters create` コマンド実行時に `--min-nodes`, `--max-nodes` でオートスケールするノードの最小数と最大数を指定

- オートスケールのトリガー<br>
    既存のノードに Pod を配置できるだけの空きリソースが残っていないとスケールアップが発動し、新たにノードが追加されます。

    Pod のリソースリクエスト数

## ■ ノード自動プロビジョニング [NAP]
ノード自動プロビジョニング [NAP] は、（ノードではなく）ノードプールをスケーリングさせるオートスケールになっている。

ノード自動プロビジョニングを有効すると、クラスタ・オートスケールも有効化されることに注意

- 設定方法<br>

- リソースの指定方法<br>
    CPU, Memory リソース等を最小数、最大数で指定できる

- オートスケールのトリガー<br>
    既存ノードのスペックが Pod の要求に合わず、同じノードをいくら増やしても Pod を配置できない場合にスケールアップが発動


## ■ 参考サイト
- https://tech.quickguard.jp/posts/gke-autoscale-overview/
- xxx