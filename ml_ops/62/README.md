# 【GCP】CloudComposer v1 を使用して簡単なワークフローを構成する

## ■ 方法

1. Cloud Composer API の有効化<br>

    - GUI で行う場合<br>
        「[GCP のコンソール画面](https://console.cloud.google.com/marketplace/product/google/composer.googleapis.com?returnUrl=%2Fcomposer%3Fhl%3Dja%26project%3Dmy-project2-303004&hl=ja&project=my-project2-303004)」から、Cloud Composer API を有効化する

    - CLI で行う場合<br>
        ```sh
        gcloud services enable composer.googleapis.com
        ```

1. Cloud Composer 環境を作成する<br>
    - GUI で行う場合<br>
        1. 「[GCP の Cloud Composer コンソール画面](https://console.cloud.google.com/composer/environments?hl=ja&project=my-project2-303004)」 にアクセスし、作成した Cloud Composer 環境を選択する
        1. 「環境を作成」->「Composer 1」ボタンをクリックする<br>
            <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170858538-01f7e8b7-9166-470a-b16f-d22d0aab544d.png">
        1. 必要な入力事項を入力後、「作成」ボタンをクリックする<br>
            <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170858676-cf5204ed-6091-4435-950e-cc49ab1c2519.png">

    - CLI で行う場合<br>
        ```sh
        gcloud composer environments create ${CLOUD_COMPOSER_ENV_NAME} \
            --location ${REGION} \
            --image-version composer-1.18.5-airflow-1.10.15
        ```
        - `--image-version` : Cloud Composer イメージの名前<br>
            CloudComposer (v1) の場合は、`composer-1.18.5-airflow-1.10.15` などを指定。CloudComposer (v2) の場合は、`composer-2.0.9-airflow-2.2.3` などを指定

1. DAG を作成する<br>
    DAG を定義した Python スクリプトを作成する。ここでは、簡単のため以下のようなスクリプトを作成する

    > - DAG（有向非巡回グラフ）<br>
    >    ワークフローは、一連の処理の流れを定義したものであるが、CloudComposer では Apache Airflow と同様に、DAG を使用してワークフローが作成される<br>
    >    DAG は、スケジューリングして実行するタスクの集合であり、それらの関係と依存関係を反映して編成される。DAG は Python スクリプトで作成され、コード上で DAG の構造（タスクとそれらの依存関係）を定義する。

    ```python
    import datetime

    import airflow
    from airflow.operators import bash_operator

    default_args = {
        'owner': 'Cloud Composer Example',
        'depends_on_past': False,
        'email': [''],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': datetime.timedelta(minutes=5),
        'start_date': datetime.datetime.now() - datetime.timedelta(days=1),
    }

    # DAG を定義
    with airflow.DAG(
            'cloud_composer_v1_dag',                        # DAG ID
            catchup=False,
            default_args=default_args,                      # タスクにデフォルト引数
            schedule_interval=datetime.timedelta(days=1)    # DAG の実行間隔
        ) as dag:

        # タスクを定義
        task_1 = bash_operator.BashOperator(
            task_id='print_dag_run_conf',               # task id
            bash_command='echo {{ dag_run.id }}'        # bash スクリプト
        )
    ```

    ポイントは、以下の通り

    - `import airflow` で Apache Airflow の Python クライアントを import する
    
    - `with airflow.DAG(...)` 内で DAG の内容を定義する。`default_args` 引数にて、DAG 内で定義したタスクを実行するために必要なデフォルト引数を設定できる

    - `with airflow.DAG(...)` 内の `bash_operator.BashOperator(...)` でタスクを定義する。`bash_operator.BashOperator(...)` で定義するタスクは、`bash_command` 引数にて bash コマンドを定義できる

        > タスクを定義するメソッドには、他にも `bash_operator.BigQueryOperator()` など様々な種類がある

    - `task_2.set_upstream(task_1)` といった形式で、t2 タスクの上流に t1 タスクをセットすることができる

1. 作成した DAG スクリプトを GCS にアップロードする<br>
    ```sh
    gcloud composer environments storage dags import \
        --environment ${CLOUD_COMPOSER_ENV_NAME}  --location ${REGION} \
        --source dag.py
    ```

    > Cloud Composer がスケジュールを設定するのは、Cloud Composer 環境の GCS バケット内の `/dags` フォルダにある DAG スクリプトファイルのみになっている。
    `gsutil` コマンドで直接 Cloud Composer 環境の GCS バケット内の `/dags` フォルダにアップロードしてもいいが、上記コマンドを使用すると、適切なパケットとフォルダに簡単にアップロードできる

1. アップロードした DAG を Airflow UI に表示する<br>
    1. 「[GCP の Cloud Composer コンソール画面](https://console.cloud.google.com/composer/environments?hl=ja&project=my-project2-303004)」 にアクセスする<br>
    1. 作成した Cloud Composer 環境の「Airflow UI を開く」ボタンをクリックする<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170860744-37399207-63ec-463f-8d4c-f9027fd7db3c.png">
    1. Airflow ツールバーで、「DAGs」ページに移動する<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170860749-6a1ec830-c977-441f-883b-b9f66f8536c5.png">
    1. 作成した DAG_ID（今回のケースでは `cloud_composer_v1_dag`）をクリックすることで、DAG のワークフローを確認できる<br>
        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/170860833-8ab14ecd-2fd4-4139-bce3-a21ca67d89e4.png">
    1. 「Graph View」タブをクリックし、作成した DAG ID を選択し、「View Log」ボタンをクリックすることで、DAG のログデータも確認できる<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170861388-12b34cfa-3a28-49a7-88fc-a89d7cf784e3.png"><br>
        <img width="800" alt="image" src="https://user-images.githubusercontent.com/25688193/170861430-201774e6-8a29-4927-a13f-385170b2fb1a.png">

1. DAG を実行する<br>
    DAG は、`schedule_interval` で設定したスケジュール間隔で自動実行されるが、それとは別に手動で実行することもできる

    - GUI で行う場合
        1. 「[GCP の Cloud Composer コンソール画面](https://console.cloud.google.com/composer/environments?hl=ja&project=my-project2-303004)」 にアクセスし、作成した Cloud Composer 環境を選択する
        1. 「DAG」タブをクリックし、作成した DAG ID をクリックする<br>
            <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170861147-4640b8be-ecd4-411b-afba-a80cf644d873.png">
        1. 「TRIGGER DAG」ボタンをクリックする<br>
            <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170861152-801b6777-6613-49dc-86a4-d6b1f9d02074.png">

    - CLI で行う場合
        ```sh
        gcloud composer environments run ${CLOUD_COMPOSER_ENV_NAME} \
            --location ${REGION} \
            dags trigger -- "cloud_composer_v1_dag"
        ```

## ■ 参考サイト
- https://cloud.google.com/composer/docs/run-apache-airflow-dag?hl=ja
- https://qiita.com/nokoxxx1212/items/77131e2a730a550f0b09#dag%E3%81%AE%E6%9B%B8%E3%81%8D%E6%96%B9%E3%81%AF
