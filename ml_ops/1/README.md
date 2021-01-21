# 【Kubeflow】 Kubeflow の基礎事項
Kubeflow は、学習用データセットの前処理、機械学習モデルの学習、機械学習モデルの推論API化といった機械学習における一連のワークフローを k8s 上で実行するためのツールである。

Kubeflow は、以下のコンポーネントで構成されている。<br>
<img src="https://user-images.githubusercontent.com/25688193/105124219-07ebb880-5b1d-11eb-99d6-69a4968b1499.png" width="550">

- Central Dashboard<br>
    各種機能を GUI 画面で表示＆作成するための機能

- Pipelines<br>
    Kubeflow 上で機械学習ワークフロー（前処理→モデルの構築→モデルの学習→モデルの推論→モデルのモニタリングなど）の構成を行うための機能

- Frameworks for Training (TensorFlow Training, PyTorch Training など）<br>
    Kubeflow 上で機械フレームワークを用いて機械学習モデルの学習を行うための機能

- Jupyter Notebooks<br>
    Kubeflow 上で Jupyter Notebooks を使用して、機械学習モデルの構築・実験などを行うための機能。

- Katib<br>
    Kubeflow 上でハイパーチューニングを行うための機能

- Feature Store (Feast)<br>
    Kubeflow 上で特徴量管理を行うための機能

- Metadata<br>
    xxx

- Fairing<br>
    xxx

- Tools for Serving<br>
    xxx

## ■ Kubeflow のインストール

<!--
### ◎ ローカル環境に Kubeflow をインストール
xxx
-->

### ◎ GKE クラスタに Kubeflow をインストール

#### ☆ kfctl を使用する場合

1. OAuth の設定をおこなう
    詳細は、参考資料「[Qiita : kubeflow(ML Pipeline Platform)を構築 on GKE](https://qiita.com/hayapher/items/522fba10b9711c638852#step3--oauth%E3%81%AE%E8%A8%AD%E5%AE%9A%E3%82%92%E3%81%8A%E3%81%93%E3%81%AA%E3%81%86)」を参照

1. ローカル環境に kfctl（kubeflow の CLI）をインストール<br>
    以下のコマンドで `kfctl` をインストールする
    ```sh
    $ ROOT_DIR=${PWD}
    $ mkdir -p kubeflow
    $ cd kubeflow
    $ curl -LO https://github.com/kubeflow/kfctl/releases/download/v1.0.1/kfctl_v1.0.1-0-gf3edb9b_darwin.tar.gz
    $ tar zxf kfctl_v1.0.1-0-gf3edb9b_darwin.tar.gz
    $ chmod +x kfctl
    $ sudo mv kfctl /usr/local/bin/kfctl
    $ cd ${ROOT_DIR}
    ```

    次に、以下のコマンドで `kfctl` コマンドが使用する環境変数を定義する
    ```sh
    $ export BASE_DIR=${ROOT_DIR}/kubeflow
    $ export PATH=${PATH}:${BASE_DIR}
    $ export KF_NAME=my-kubeflow
    $ export KF_DIR=${BASE_DIR}/${KF_NAME}
    $ export CONFIG_URI="https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_gcp_iap.v1.0.1.yaml"
    $ export CLIENT_ID=<CLIENT_ID from OAuth page>
    $ export CLIENT_SECRET=<CLIENT_SECRET from OAuth page>
    ```
    - `${KF_DIR}` : kubeflow が自動で生成する各種 kubernetes 用設定ファイル（＝マニフェストファイル）*.yaml を格納する場所
    - `${CONFIG_URI}` : kubeflow をデプロイするときのコンフィグファイル。構築する KubeFlow の構成（認証機能あり、なし）や構築場所（AWS、Azure、GCP、既存Kubernetes）によってファイルパスを変える必要がある。
        - `kfctl_k8s_istio.v*.yaml` : kfctl_k8s_istio 使用時
        - `kfctl_gcp_iap.v*.yaml` : GCP 使用時（認証付き）
    - `${CLIENT_ID}` : OAuth の設定の際に生成した Client ID
    - `${CLIENT_SECRET}` : 

1. GKE 上に k8s クラスタを構築<br>
    ```sh
    $ gcloud container clusters create ${CLUSTER_NAME} \
        --num-nodes=${NUM_NODES}
    ```

1. `kfctl apply` コマンドで k8s クラスタに kubeflow をデプロイする<br>
    `kfctl_env.sh` で定義した環境変数を元に、以下のコマンドで k8s クラスタに kubeflow をデプロイする（=kubeflow の Pod と Service を作成する）
    ```sh
    $ rm -rf ${KF_DIR}
    $ mkdir -p ${KF_DIR}
    $ cd ${KF_DIR}
    $ kfctl apply -V -f ${CONFIG_URI}
    $ cd ${ROOT_DIR}
    ```

1. デプロイした kubeflow の Pod と Service が正常に起動しているか確認する<br>
    デプロイした kubeflow の全ての Pod は、以下のコマンドか GKE の GUI 画面（ワークロード）から確認可能。全ての Pod が正常に起動されていれば OK
    ```sh
    $ kubectl get pod --all-namespaces
    ```

    デプロイした kubeflow の全ての Service は、以下のコマンドか GKE の GUI 画面（Service と Ingress）から確認可能。全ての Service が正常に起動されていれば OK
    ```sh
    $ kubectl get services --all-namespaces
    ```

1. Kubeflow の Central Dashboard にアクセス<br>
    ```sh
    $ kubectl port-forward -n istio-system svc/istio-ingressgateway 80:80 --address 0.0.0.0
    ```

#### ☆ ksonnet を使用する場合
> ksonnet : <br>
> k8s のマニフェストファイル管理ツール。k8s のマニフェストファイル yaml を用意して `kubectl create -f xxx.yaml` する代わりに、`ks pkg install xxx` だけでデプロイができるようになる。

1. ローカル環境に ksonnet をインストール
1. GKE 上に k8s クラスタを構築
1. `ks apply` で k8s クラスタに kubeflow をデプロイする
1. Kubernetes ダッシュボードにアクセス

### ◎ Google AI Platform Pipelines を利用した Kubeflow Pipelines のインストール
xxx

## ■ KubeFlow Pipelines の構成
xxx

## ■ 参考文献
- https://qiita.com/hayapher/items/522fba10b9711c638852
- https://qiita.com/Hiroyuki_OSAKI/items/9ab5cbbcb9365eed7fc5
- https://ymym3412.hatenablog.com/entry/2020/01/07/051653
- https://techblog.zozo.com/entry/aip-pipelines-impl
