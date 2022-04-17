# 【Vertex AI】Vertex Pipelines を使用して機械学習パイプラインを構築する

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
    Vertex AI Pipelines は Cloud Storage を使用して、パイプライン実行に必要なアーティファクト（学習用データセット・学習済みモデル・エンドポイントなど）を保存するので、予め GCS パケットを作成し、上記作成した Vertex Pipelines 用のサービスアカウントにパケットへのアクセス権を付与しておく。

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
    Kubeflow Pipelines SDK を使用してパイプラインを構築するために、[Kubeflow Pipelines SDK](https://www.kubeflow.org/docs/components/pipelines/sdk/install-sdk/) v1.8.9 以降（v1.7.2以降が Kubeflow Pipelines SDK v2 扱い）をインストールする
    ```sh
    $ pip3 install kfp
    ```

    > Vertex AI を使用する場合でも、Kubeflow の Kubeflow Pipelines SDK を使用して、パイプラインのコードを実装する形式になる

    > Vertex Pipeline は、Kubeflow Pipelines SDK v2 のみ対応していることに注意

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
    import argparse
    import kfp
    from google.cloud import aiplatform
    import google.cloud.aiplatform as aip
    from google_cloud_pipeline_components import aiplatform as gcc_aip


    # Pipeline を構築する関数には @kfp.dsl.pipeline デコレータを付与する
    # @kfp.dsl.pipelineデコレータを付与した関数への引数は、PipelineからRunを生成する際に外挿するパラメータとなります。
    # pipeline_root : Vertex AI用サービスアカウントがアクセスできるGCSパケットパス
    @kfp.dsl.pipeline(name='automl-image-training-v2', pipeline_root="gs://vertex-ai-bucket-360")
    def make_pipeline(
        project_id: str = "my-project2-303004",
    ):
      #---------------------------------------------------
      # データセットの作成
      #---------------------------------------------------
      # データセットを作成する。
      # パイプライン実行時に、このデータセットは GCSパケット（今回のケースでは、"gs://vertex-ai-bucket-360"）に保管される。
      # 尚、戻り値の `ds_op` は出力の定義のみを格納し、実際に実行されて返されるオブジェクトは格納しないことに注意。
      # オブジェクトの値は、dsl.pipeline　レベルではアクセスできず、下流のコンポーネントの入力として提供することで初めて取得できる。
        ds_op = gcc_aip.ImageDatasetCreateOp(
            project=project_id,
            display_name="flowers",
            gcs_source="gs://cloud-samples-data/vision/automl_classification/flowers/all_data_v2.csv",	# 今回の例では、予め用意されているデータセットを使用する
            import_schema_uri=aiplatform.schema.dataset.ioformat.image.single_label_classification,
        )

      #---------------------------------------------------
      # 前処理
      #---------------------------------------------------

      #---------------------------------------------------
      # モデルの学習処理
      #---------------------------------------------------
      # AutoML モデルを作成し、学習する
      # 学習済みモデルは GCSパケット（今回のケースでは、"gs://vertex-ai-bucket-360"）に保管される。
        training_job_run_op = gcc_aip.AutoMLImageTrainingJobRunOp(
            project=project_id,
            display_name="train-iris-automl-mbsdk-1",
            prediction_type="classification",						# 分類モデルにする
            model_type="CLOUD",										# str = "CLOUD" 必須。Image Classification のデフォルト値
            #base_model=None,										# 
            dataset=ds_op.outputs["dataset"],						# 学習用データセット
            model_display_name="iris-classification-model-mbsdk",
            training_fraction_split=0.6,
            validation_fraction_split=0.2,
            test_fraction_split=0.2,
            budget_milli_node_hours=8000,
        )

      #---------------------------------------------------
      # モデルの推論処理
      #---------------------------------------------------

      #---------------------------------------------------
      # 学習済みモデルのデプロイして REST API として利用可能にする
      #---------------------------------------------------
        # REST API での推論用エンドポイントを作成
        create_endpoint_op = gcc_aip.EndpointCreateOp(
            project=project_id,
            display_name = "create-endpoint",
        )

      # 学習済みモデルをデプロイする
        model_deploy_op = gcc_aip.ModelDeployOp(
            model=training_job_run_op.outputs["model"],			# 学習済みモデルを設定
            endpoint=create_endpoint_op.outputs['endpoint'],	# エンドポイントを設定
            automatic_resources_min_replica_count=1,			# 最小オートスケーリング数？
            automatic_resources_max_replica_count=1,			# 西田オートスケーリング数?
        )

        return

    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument('--project_id', type=str, default="my-project2-303004", help="GCSプロジェクトID")
        parser.add_argument('--pipeline_root_path', type=str, default="gs://vertex-ai-bucket-360", help="Vertex AI用サービスアカウントがアクセスできるGCSパケットパス")
        parser.add_argument('--pipeline_json_path', type=str, default="image_classif_pipeline.json", help="Vertex AI用サービスアカウントがアクセスできるGCSパケットパス")
        parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
        args = parser.parse_args()
        if( args.debug ):
            for key, value in vars(args).items():
                print('%s: %s' % (str(key), str(value)))

        # パイプラインを定義する JSON ファイルを生成
        kfp.v2.compiler.Compiler().compile(
        pipeline_func = make_pipeline, 
        package_path = args.pipeline_json_path
      )

        # Vertex AI Python クライアントを使用して JSON 化したパイプラインを送信し、実行する
      # 送信したパイプラインと実行状態は、Vertex AI　のコンソール画面から確認できる
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
          #---------------------------------------------------
          # データセットの作成
          #---------------------------------------------------
          # データセットを作成する。
          # パイプライン実行時に、このデータセットは GCSパケット（今回のケースでは、"gs://vertex-ai-bucket-360"）に保管される。
          # 尚、戻り値の `ds_op` は出力の定義のみを格納し、実際に実行されて返されるオブジェクトは格納しないことに注意。
          # オブジェクトの値は、dsl.pipeline　レベルではアクセスできず、下流のコンポーネントの入力として提供することで初めて取得できる。
            ds_op = gcc_aip.ImageDatasetCreateOp(
                project=project_id,
                display_name="flowers",
                gcs_source="gs://cloud-samples-data/vision/automl_classification/flowers/all_data_v2.csv",	# 今回の例では、予め用意されているデータセットを使用する
                import_schema_uri=aiplatform.schema.dataset.ioformat.image.single_label_classification,
            )

          #---------------------------------------------------
          # 前処理
          #---------------------------------------------------

          #---------------------------------------------------
          # モデルの学習処理
          #---------------------------------------------------
          # AutoML モデルを作成し、学習する
          # 学習済みモデルは GCSパケット（今回のケースでは、"gs://vertex-ai-bucket-360"）に保管される。
            training_job_run_op = gcc_aip.AutoMLImageTrainingJobRunOp(
                project=project_id,
                display_name="train-iris-automl-mbsdk-1",
                prediction_type="classification",						# 分類モデルにする
                model_type="CLOUD",										# str = "CLOUD" 必須。Image Classification のデフォルト値
                #base_model=None,										# 
                dataset=ds_op.outputs["dataset"],						# 学習用データセット
                model_display_name="iris-classification-model-mbsdk",
                training_fraction_split=0.6,
                validation_fraction_split=0.2,
                test_fraction_split=0.2,
                budget_milli_node_hours=8000,
            )

          #---------------------------------------------------
          # モデルの推論処理
          #---------------------------------------------------

          #---------------------------------------------------
          # 学習済みモデルのデプロイして REST API として利用可能にする
          #---------------------------------------------------
            # REST API での推論用エンドポイントを作成
            create_endpoint_op = gcc_aip.EndpointCreateOp(
                project=project_id,
                display_name = "create-endpoint",
            )

          # 学習済みモデルをデプロイする
            model_deploy_op = gcc_aip.ModelDeployOp(
                model=training_job_run_op.outputs["model"],			# 学習済みモデルを設定
                endpoint=create_endpoint_op.outputs['endpoint'],	# エンドポイントを設定
                automatic_resources_min_replica_count=1,			# 最小オートスケーリング数？
                automatic_resources_max_replica_count=1,			# 西田オートスケーリング数?
            )

            return
        ```

        `@kfp.dsl.pipeline` デコレータを付与したメソッドで、パイプラインの内容を定義する。
        パイプラインの構成は、一般的に「データセット作成 -> 前処理 -> モデルの定義＆学習 -> モデルの推論 -> モデルのデプロイ& REST API 化」という流れになるが、今回のケースでは、前処理と推論処理はなしにしている

        また、簡単のため、データセットは予め用意されているデータセットを使用し、モデルの AutoML モデルを使用している

        > Kubeflow では、`@dsl.pipeline(...)` を使用していたが、`@kfp.dsl.pipeline(...)` を使用していることに注意

        > 独自のパイプラインコンポーネントを使用したい場合は、コンポーネントでの入出力や docker image などを定義した yaml ファイル `component.yaml` を作成する形式になるが、今回の例では簡単のため、デフォルトにあるデータセットと AutoML モデルを使用してパイプラインを構築している。

    1. パイプラインのコードを JSON ファイルに変換
        ```python
        # パイプラインを定義する JSON ファイルを生成
        kfp.v2.compiler.Compiler().compile(
            pipeline_func = make_pipeline, 
            package_path = args.pipeline_json_path
        )
        ```

        > Kubeflow では、`kfp.compiler` を使用していたが、`kfp.v2.compiler` を使用していることに注意

    1. Vertex AI Python クライアントを使用して JSON 化したパイプラインを送信し、パイプラインを実行する
        ```python
        # Vertex AI Python クライアントを使用して JSON 化したパイプラインを送信し、パイプラインを実行する
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
    「[Vertex AI のパイプラインコンソール画面](https://console.cloud.google.com/vertex-ai/pipelines?hl=ja&project=my-project2-303004)」から、構築したパイプラインを確認する

    <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/163700041-dd686983-5dfb-47cd-b794-fdf5792d9b2f.png">

1. モデルのエンドポイントを呼び出し、推論処理を行う<br>
    パイプラインの実行完了後、以下のような `curl` コマンドで、デプロイした学習済みモデルのエンドポイント `https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/endpoints/${ENDPOINT_ID}:predict` を呼び出し、推論処理を行う。<br>
    尚、デプロイしたモデルのエンドポイントの情報（`ENDPOINT_ID` など）は、「[Vertex AI のエンドポイントコンソール画面](https://console.cloud.google.com/vertex-ai/endpoints?hl=ja&project=my-project2-303004)」から確認できる

    ```sh
    PROJECT_ID="my-project2-303004"
    ENDPOINT_ID="979788005650726912"
    INPUT_DATA_FILE="test.json"

    curl \
      -X POST \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/json" https://us-central1-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/us-central1/endpoints/${ENDPOINT_ID}:predict \
      -d "@${INPUT_DATA_FILE}"
    ```

    - `${INPUT_DATA_FILE}` の例
        ```json
        {
          "instances": [
            { "instance_key_1": "value", ... }, ...
          ],
          "parameters": { "parameter_key_1": "value", ... }, ...
        }
        ```

## ■ 参考サイト

- https://cloud.google.com/vertex-ai/docs/pipelines?hl=ja
- https://cam-inc.co.jp/p/techblog/582520922968163131
