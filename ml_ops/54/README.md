# Vertex Pipelines を使用して機械学習パイプラインを構築する

## ■ 方法

1. Vertex AI and Cloud Storage API を有効化する<br>
  [GCPコンソール画面](https://console.cloud.google.com/apis/enableflow?apiid=aiplatform.googleapis.com,storage-component.googleapis.com&hl=ja&_ga=2.23110394.1149610791.1649935695-351711596.1649935626&project=my-project2-303004) から、Vertex AI and Cloud Storage API を有効化する

1. Vertex Pipelines 用のサービスアカウントを作成する<br>
    Vertex Pipelines 用のサービスアカウントを作成する。  

    ```sh
    #!/bin/sh
    #set -eu
    ROOT_DIR=${PWD}
    PROJECT_ID=my-project2-303004
    SERVICE_ACCOUNT_NAME=vertex-ai

    if [ ! -e "key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
        # サービスアカウント作成権限のある個人アカウントに変更
        gcloud auth login

        # サービスアカウントを作成する
        if [ ! "$(gcloud iam service-accounts list | grep ${SERVICE_ACCOUNT_NAME})" ] ;then
            gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME}
        fi

        # サービスアカウントに必要な権限を付与する
        gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/aiplatform.user"

        gcloud projects add-iam-policy-binding ${PROJECT_ID} --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"

        # サービスアカウントの秘密鍵 (json) を生成する
        if [ ! -e "key/${SERVICE_ACCOUNT_NAME}.json" ] ; then
            mkdir -p key
            gcloud iam service-accounts keys create key/${SERVICE_ACCOUNT_NAME}.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
        fi

        # 作成した json 鍵を環境変数に反映
        #export GOOGLE_APPLICATION_CREDENTIALS="key/{SERVICE_ACCOUNT_NAME}.json"
        #gcloud auth activate-service-account SERVICEACCOUNTNAME@{PROJECT_ID}.iam.gserviceaccount.com --key-file ROOTDIR/api/key/{SERVICE_ACCOUNT_NAME}.json
        #gcloud auth list
    fi
    ```

    > 作成したサービスアカウントに Vertex AI へのアクセス権を付与するためには、`--role` に `"roles/aiplatform.user"` を設定すればよい

    > サービスアカウントを使用して Vertex AI Pipelines でパイプラインを実行するには、`--role` に `"roles/roles/iam.serviceAccountUser"` を追加する必要がある
    
    > パイプラインで使用するその他 GCS リソースがある場合は、`--role` にその GCS リソースの値を追加する必要がある

1. Vertex AI Pipelines 用の GCS パケットを作成する<br>
    Vertex AI Pipelines は Cloud Storage を使用して、パイプライン実行に必要なーティファクトを保存するので、予め GCS パケットを作成し、上記作成した Vertex Pipelines 用のサービスアカウントにパケットへのアクセス権を付与しておく。

    ```sh
    if [ ! "$(gsutil list | grep "gs://${GCS_BUCKET_NAME}/")" ] ;then
        # GCS パケットを作成する
        gsutil mb -p ${PROJECT_ID} gs://${GCS_BUCKET_NAME}/

        # Vertex AI 用サービスアカウントに作成した GCS パケットへの読み書きアクセス権限を付与
        gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com:roles/storage.objectCreator,objectViewer gs://${GCS_BUCKET_NAME}
        gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com:roles/storage.objectViewer gs://${GCS_BUCKET_NAME}
    fi
    ```

1. Kubeflow Pipelines SDK をインストールする<br>
    Kubeflow Pipelines SDK を使用してパイプラインを構築するために、[Kubeflow Pipelines SDK](https://www.kubeflow.org/docs/components/pipelines/sdk/install-sdk/) v1.8.9 以降をインストールする
    ```sh
    $ pip3 install kfp
    ```

    > Vertex AI を使用する場合でも、Kubeflow の Kubeflow Pipelines SDK を使用して、パイプラインのコードを実装する形式になる

1. Vertex AI SDK をインストールする<br>
    パイプラインで Vertex AI Python クライアントを使用するために、[Vertex AI SDK](https://github.com/googleapis/python-aiplatform) v1.7 以降をインストールする。
    ```sh
    $ pip3 install google-cloud-aiplatform
    ```

1. Kubeflow の Google Cloud Pipeline Components をインストールする
    パイプラインで Vertex AI サービスを使用するために、[Kubeflow の Google Cloud Pipeline Components](https://github.com/kubeflow/pipelines/tree/master/components/google-cloud#installation) をインストールする。
    ```sh
    $ pip3 install -U google-cloud-pipeline-components
    ```

1. パイプラインのコードを実装する<br>
    Kubeflow Pipelines SDK, Vertex AI SDK, Google Cloud Pipeline Components を使用して、パイプラインのコードを実装する

    ```python
    ```

1. パイプラインのコードを JSON ファイルにコンパイルするコードを実装する
    ```python
    from kfp.v2 import compiler
    compiler.Compiler().compile(pipeline_func=pipeline, package_path='image_classif_pipeline.json')
    ```

1. xxx


## ■ 参考サイト

- https://cloud.google.com/vertex-ai/docs/pipelines?hl=ja
