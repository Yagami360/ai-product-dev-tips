# <In-progress>【Kubeflow】GKE クラスタに Kubeflow を構築する

> 現状この方法では、以下のエラーがでてうまくインストールできない。
> Kubeflow Pipelines を使用するだけなら、「[Kubeflow】Google AI Platform Pipelines を利用して Kubeflow Pipelines の構築する](https://github.com/Yagami360/MachineLearning_PreProcessing_Exercises/tree/master/ml_ops/3)」 での方法のほうが圧倒的に簡単

```sh
INFO[0017] Updating kubeflow-cluster-storage status: RUNNING (op = operation-1611310888974-5b97a8d28f85d-07c2a090-5869c891)  filename="gcp/gcp.go:390"
ERRO[0022] Updating kubeflow-cluster-storage error: &{Code:NO_METHOD_TO_UPDATE_FIELD Location: Message:No method found to update field 'zone' on resource 'kubeflow-cluster-storage-metadata-store' of type 'compute.v1.disk'. The resource may need to be recreated with the new field. ForceSendFields:[] NullFields:[]}  filename="gcp/gcp.go:386"
ERRO[0022] Updating kubeflow-cluster-storage error: &{Code:NO_METHOD_TO_UPDATE_FIELD Location: Message:No method found to update field 'https' on resource 'kubeflow-cluster-storage-metadata-store' of type 'compute.v1.disk'. The resource may need to be recreated with the new field. ForceSendFields:[] NullFields:[]}  filename="gcp/gcp.go:386"
ERRO[0022] Updating kubeflow-cluster-storage error: &{Code:NO_METHOD_TO_UPDATE_FIELD Location: Message:No method found to update field 'zone' on resource 'kubeflow-cluster-storage-artifact-store' of type 'compute.v1.disk'. The resource may need to be recreated with the new field. ForceSendFields:[] NullFields:[]}  filename="gcp/gcp.go:386"
ERRO[0022] Updating kubeflow-cluster-storage error: &{Code:NO_METHOD_TO_UPDATE_FIELD Location: Message:No method found to update field 'https' on resource 'kubeflow-cluster-storage-artifact-store' of type 'compute.v1.disk'. The resource may need to be recreated with the new field. ForceSendFields:[] NullFields:[]}  filename="gcp/gcp.go:386"
INFO[0022] Updating kubeflow-cluster-storage status: RUNNING (op = operation-1611310888974-5b97a8d28f85d-07c2a090-5869c891)  filename="gcp/gcp.go:390"
ERRO[0029] Updating kubeflow-cluster-storage error: &{Code:NO_METHOD_TO_UPDATE_FIELD Location: Message:No method found to update field 'zone' on resource 'kubeflow-cluster-storage-metadata-store' of type 'compute.v1.disk'. The resource may need to be recreated with the new field. ForceSendFields:[] NullFields:[]}  filename="gcp/gcp.go:386"
ERRO[0029] Updating kubeflow-cluster-storage error: &{Code:NO_METHOD_TO_UPDATE_FIELD Location: Message:No method found to update field 'https' on resource 'kubeflow-cluster-storage-metadata-store' of type 'compute.v1.disk'. The resource may need to be recreated with the new field. ForceSendFields:[] NullFields:[]}  filename="gcp/gcp.go:386"
ERRO[0029] Updating kubeflow-cluster-storage error: &{Code:NO_METHOD_TO_UPDATE_FIELD Location: Message:No method found to update field 'zone' on resource 'kubeflow-cluster-storage-artifact-store' of type 'compute.v1.disk'. The resource may need to be recreated with the new field. ForceSendFields:[] NullFields:[]}  filename="gcp/gcp.go:386"
ERRO[0029] Updating kubeflow-cluster-storage error: &{Code:NO_METHOD_TO_UPDATE_FIELD Location: Message:No method found to update field 'https' on resource 'kubeflow-cluster-storage-artifact-store' of type 'compute.v1.disk'. The resource may need to be recreated with the new field. ForceSendFields:[] NullFields:[]}  filename="gcp/gcp.go:386"
Error: failed to apply:  (kubeflow.error): Code 500 with message: coordinator Apply failed for gcp:  (kubeflow.error): Code 400 with message: gcp apply could not update deployment manager Error could not update deployment manager entries; Updating kubeflow-cluster-storage error(400): BAD REQUEST
Usage:
  kfctl apply -f ${CONFIG} [flags]

Flags:
  -f, --file string   Static config file to use. Can be either a local path:
                                export CONFIG=./kfctl_gcp_iap.yaml
                        or a URL:
                                export CONFIG=https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_gcp_iap.v1.0.0.yaml
                                export CONFIG=https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_istio_dex.v1.0.0.yaml
                                export CONFIG=https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_aws.v1.0.0.yaml
                                export CONFIG=https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_k8s_istio.v1.0.0.yaml
                        kfctl apply -V --file=${CONFIG}
  -h, --help          help for apply
  -V, --verbose       verbose output default is false

failed to apply:  (kubeflow.error): Code 500 with message: coordinator Apply failed for gcp:  (kubeflow.error): Code 400 with message: gcp apply could not update deployment manager Error could not update deployment manager entries; Updating kubeflow-cluster-storage error(400): BAD REQUEST
```

## ■ kfctl を使用する場合

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
    kubeflow では GPU を使用するので GPU 有りでの GKE クラスタを構築する必要があることに注意
    ```sh
    $ gcloud container clusters create ${CLUSTER_NAME} \
        --machine-type=${CPU_TYPE} \
        --accelerator type=${GPU_TYPE},count=1 \
        --num-nodes=${NUM_NODES}
    ```
    - `${CPU_TYPE}` : CPU の種類（`n1-standard-1`, `n1-standard-4` など）
    - `${GPU_TYPE}` : GPU の種類（`nvidia-tesla-k80`, `nvidia-tesla-t4` など）

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

## ■ ksonnet を使用する場合
> ksonnet : <br>
> k8s のマニフェストファイル管理ツール。k8s のマニフェストファイル yaml を用意して `kubectl create -f xxx.yaml` する代わりに、`ks pkg install xxx` だけでデプロイができるようになる。

1. ローカル環境に ksonnet をインストール
1. GKE 上に k8s クラスタを構築
1. `ks apply` で k8s クラスタに kubeflow をデプロイする
1. Kubernetes ダッシュボードにアクセス

## ■ 参考文献
- 公式 : https://www.kubeflow.org/docs/gke/deploy/
- https://qiita.com/hayapher/items/522fba10b9711c638852
- https://qiita.com/Hiroyuki_OSAKI/items/9ab5cbbcb9365eed7fc5
- https://ymym3412.hatenablog.com/entry/2020/01/07/051653
