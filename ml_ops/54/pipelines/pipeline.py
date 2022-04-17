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
