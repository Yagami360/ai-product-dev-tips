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

    ポイントは、以下の通り

    1. パイプラインの内容を定義
        ```python
        # Pipeline を構築する関数には @kfp.dsl.pipeline デコレータを付与する
        # @kfp.dsl.pipelineデコレータを付与した関数への引数は、PipelineからRunを生成する際に外挿するパラメータとなります。
        # pipeline_root : Vertex AI用サービスアカウントがアクセスできるGCSパケットパス
        @kfp.dsl.pipeline(name='automl-image-training-v2', pipeline_root="gs://vertex-ai-bucket-360")
        def make_pipeline(
            project_id: str = "my-project2-303004",
        ):
            # The first step of your workflow is a dataset generator.
            # This step takes a Google Cloud pipeline component, providing the necessary
            # input arguments, and uses the Python variable `ds_op` to define its
            # output. Note that here the `ds_op` only stores the definition of the
            # output but not the actual returned object from the execution. The value
            # of the object is not accessible at the dsl.pipeline level, and can only be
            # retrieved by providing it as the input to a downstream component.
            ds_op = gcc_aip.ImageDatasetCreateOp(
                project=project_id,
                display_name="flowers",
                gcs_source="gs://cloud-samples-data/vision/automl_classification/flowers/all_data_v2.csv",
                import_schema_uri=aiplatform.schema.dataset.ioformat.image.single_label_classification,
            )

            # The second step is a model training component. It takes the dataset
            # outputted from the first step, supplies it as an input argument to the
            # component (see `dataset=ds_op.outputs["dataset"]`), and will put its
            # outputs into `training_job_run_op`.
            training_job_run_op = gcc_aip.AutoMLImageTrainingJobRunOp(
                project=project_id,
                display_name="train-iris-automl-mbsdk-1",
                prediction_type="classification",
                model_type="CLOUD",
                #base_model=None,
                dataset=ds_op.outputs["dataset"],
                model_display_name="iris-classification-model-mbsdk",
                training_fraction_split=0.6,
                validation_fraction_split=0.2,
                test_fraction_split=0.2,
                budget_milli_node_hours=8000,
            )

            # The third and fourth step are for deploying the model.
            create_endpoint_op = gcc_aip.EndpointCreateOp(
                project=project_id,
                display_name = "create-endpoint",
            )

            model_deploy_op = gcc_aip.ModelDeployOp(
                model=training_job_run_op.outputs["model"],
                endpoint=create_endpoint_op.outputs['endpoint'],
                automatic_resources_min_replica_count=1,
                automatic_resources_max_replica_count=1,
            )

            return
        ```

        > Kubeflow では、`@dsl.pipeline(...)` を使用していたが、`@kfp.dsl.pipeline(...)` を使用していることに注意

    1. パイプラインのコードを JSON ファイルに変換
        ```python
        # パイプラインを定義する JSON ファイルを生成
        kfp.v2.compiler.Compiler().compile(
            pipeline_func = make_pipeline, 
            package_path = args.pipeline_json_path
        )
        ```

        > Kubeflow では、`kfp.compiler` を使用していたが、`kfp.v2.compiler` を使用していることに注意

    1. Vertex AI Python クライアントを使用して JSON 化したパイプラインを送信する
        ```python
        # Vertex AI Python クライアントを使用して JSON 化したパイプラインを送信する
        job = aip.PipelineJob(
            display_name="automl-image-training-v2",
            template_path=args.pipeline_json_path,
            pipeline_root=args.pipeline_root_path,
            parameter_values={
                'project_id': args.project_id
            }
        )
        job.submit()
        ```

1. Vertex AI のコンソール画面を確認する<br>
    [Vertex AI のパイプラインコンソール画面](https://console.cloud.google.com/vertex-ai/pipelines?hl=ja&project=my-project2-303004) から、構築したパイプラインを確認する


## ■ 参考サイト

- https://cloud.google.com/vertex-ai/docs/pipelines?hl=ja
