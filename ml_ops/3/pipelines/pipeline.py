import kfp
from kfp import dsl

# Pipeline を構築する関数には @dsl.pipeline デコレータを付与する
# @dsl.pipelineデコレータを付与した関数への引数は、PipelineからRunを生成する際に外挿するパラメータとなります。
@dsl.pipeline(
  name='Download dataset pipeline',
  description='Download dataset from gcs storage.'
)
def make_pipeline(
    project_id = "myproject-292103", bucket_name = "ml_dataset_360", dataset_dir = "gs://ml_dataset_360",
):
    # dsl.ContainerOp に実行する Docker Image やコンテナで実行するコマンドや引数を指定することで Component を生成できる
    download_op = dsl.ContainerOp(
        name='download_from_gcs',
        image='gcr.io/myproject-292103/pipeline-image:latest',
        command=['python3', 'download_dataset_from_gcs.py'],
        arguments=[
                '--project_id', project_id,
                '--bucket_name', bucket_name,
                '--dataset_dir', dataset_dir,
                '--debug', True,
        ],
        file_outputs={                      # 下流(downstream)のタスクにデータを受け渡したいときは、ファイルに書き出してそのパスをfile_outputsに渡すと値を渡せる
                    'output': '/output.txt',
        }
    )

    output = download_op.outputs['output']
    return

if __name__ == '__main__':
    # Pipelineを定義するYAMLを生成
    kfp.compiler.Compiler().compile(make_pipeline, __file__ + '.yaml')
