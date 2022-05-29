# 【GCP】CloudComposer の基礎事項

GCP のワークフローサービス（一連の処理の流れを定義して動作させるサービス）で、Apache Airflow を基に構築されている。
Apache Airflow と比較して、以下のようなメリットがある

> - Apache Airflow<br>
>   有向非巡回グラフ（DAG)を応用したワークフローサービス。


- フルマネージドサービスなので、インストールや管理の手間なしに、Airflow 活用できる
- オーケストレーション（システムやサービスにおける設定や管理の自動化）が容易
- 他の GCP サービスとの連携が容易

CloudComposer は、以下のようなコンポーネントから構成される

- DAG（有向非巡回グラフ）<br>
    ワークフローは、一連の処理の流れを定義したものであるが、CloudComposer では Apache Airflow と同様に、DAG を使用してワークフローが作成される<br>

    DAG は、スケジューリングして実行するタスクの集合であり、それらの関係と依存関係を反映して編成される。DAG は以下のような Python スクリプトで作成され、コード上で DAG の構造（タスクとそれらの依存関係）を定義する。

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
            'cloud_composer_v1_dag',                        # DAG の名前
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

- タスク<br>
    DAG 内で定義される、実際の処理の塊。タスクは、`bash_operator.BashOperator()` などの Operator で定義する

CloudComposer のバージョンには、v1 と v2 がある

- CloudComposer v1<br>
    - Airflow 1 or 2 で動作する
    - Standard GKE で動作する
    - 自動で水平スケーリングできない

- CloudComposer v2<br>
    - Airflow 2 でのみ動作する
    - Autopilotモードの GKE で動作する
    - 自動で水平スケーリングできる

## ■ 参考サイト
- https://www.topgate.co.jp/cloud-composer
- https://cloud.google.com/composer/docs/concepts/overview?hl=ja
- https://qiita.com/minarai/items/28b4269736ea0df136ff#cloud-composer%E7%B7%A8
- https://medium.com/eureka-engineering/data-mgmt-cloud-composer-29ba3fcbffe0