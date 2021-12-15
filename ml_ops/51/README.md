# 【GKE】k8s の Job を使用する

Job は1つ以上の Pod を作成し、指定された数（＝完了数）の Pod が正常に終了するのを保証する k8s リソースである。指定された数の Pod が全て正常終了した際に Job が完了となり、それ以降 Pod は動作しなくなる。

Job には、並列数と完了数（＝正常終了する回数）を設定できるが、その動作イメージ（完了数：５、並列数：３の場合）は、以下の図のようになる。

<img src="https://user-images.githubusercontent.com/25688193/146134162-9e709fff-b78d-4554-9249-0685968e3a06.png" width="500"><br>


> k8s の Job は、一般的にスクリプトの起動から終了までが記述された Pod を管理する。そのため、FastAPI などを使用した REST API のように、常にスクリプトが起動しているタイプの Pod 管理には不向き？

## ■ 方法

1. Job の処理内容を定義したスクリプトを作成する<br>
    ここでは簡単な例として、処理時間が 10sec で、90% の確率で正常終了、10% の確率で異常終了するスクリプトを作成する。

    ```python
    import os
    import sys
    from datetime import datetime
    from time import sleep
    import random
    import logging

    # logger
    if not os.path.isdir("log"):
        os.mkdir("log")
    #if( os.path.exists(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log')) ):
    #    os.remove(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
    logger = logging.getLogger(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
    logger.setLevel(10)
    logger_fh = logging.FileHandler(os.path.join("log",os.path.basename(__file__).split(".")[0] + '.log'))
    logger.addHandler(logger_fh)

    #
    if __name__ == "__main__":
        logger.info('[{}] time {} | 処理開始しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
        sleep(10)
        if( random.uniform(0, 1) <= 0.9 ):
            logger.info('[{}] time {} | 正常終了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
            sys.exit(0)
        else:
            logger.info('[{}] time {} | 異常終了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
            sys.exit(1)
    ```

    > k8s 側での Job の正常終了 or 異常終了の判定は、スクリプトの戻り値の `sys.exit(0)` or `sys.exit(1)` を元に行っている点に注目

    > FastAPI などを使用した REST API でのスクリプトの場合は、どうやって正常終了 or 異常終了を k8s に認証させるのか？

1. k8s のマニフェストファイルを作成する<br>
    ```yaml
    # Job
    apiVersion: batch/v1
    kind: Job
    metadata:
      name: sample-job
    spec:
      completions: 10           # 正常終了する回数
      parallelism: 2            # Jobで同時にPodを実行できる並列数
      backoffLimit: 5           # 失敗したJobのリトライ回数（デフォルト6）
      template:                 # Job で実行する Pod の Template
        spec:
          containers:
          - name: sample-job-container
            image: gcr.io/my-project2-303004/sample-job-image-gke:latest
            command: ["/bin/sh","-c"]
            args: ["python job.py"]
          restartPolicy: Never  # コンテナが失敗した際の再起動のポリシー（OnFailure : 失敗時のみコンテナを再起動、Never : コンテナを再起動しない）。JOBを使用した場合で Never を設定すると、Pod がエラーになった際にはJobが新しいPodを作成して実行してくれる。
    ```

    ポイントは、以下の通り

    - `kind: Job` で Job リソースを定義する

    - `spec.completions` で、正常終了する回数を指定する

    - `spec.parallelism` で、Jobで同時にPodを実行できる並列数を指定する

    - `spec.template` には、Deployment リソース定義時と同じように、コンテナ定義を行う。

    - `spec.template.restartPolicy` には、コンテナが失敗した際の再起動のポリシーを定義する
      - `OnFailure` : 失敗時のみコンテナを再起動
      - `Never` : コンテナを再起動しない。Job を使用する場合で Never を設定すると、Pod がエラーになった際には Job が新しいPodを作成して実行してくれる。

1. Job を定義したマニフェストファイルをデプロイし、Job を実行する
    ```sh
    $ kubectl apply -f k8s/job.yml
    ```

    > ジョブの実行は、このマニフェストファイルをデプロイした時点で行われることに注意

    > FastAPI などを使用した REST API の場合は、リクエスト処理受付時に API の処理が開始されるが、REST API での処理を k8s の Job で構成する場合は、どのタイミングやどこからで 上記デプロイコマンドを行えばよいのか？

1. Job と Pod の動作を確認する
    ```sh
    $ kubectl get pods
    $ kubectl get job 
    ```

    <img src="https://user-images.githubusercontent.com/25688193/146132883-c9714c60-9060-46e0-adc1-02c2816a4c33.png" width="700"><br>

## ■ 参照サイト

- https://engineering.mercari.com/blog/entry/k8s-cronjob-20200908/
- https://cstoku.dev/posts/2018/k8sdojo-14/