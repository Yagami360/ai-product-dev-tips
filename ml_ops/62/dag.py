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
