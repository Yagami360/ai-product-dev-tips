# 【BigQuery】BigQuery を使用したデータ処理（CLI 使用時）
BigQuery の CLI での処理は、gcloud コマンドインストール時にインストールされている `bq` コマンドを用いて行うことができる。

## ■ 事前準備

1. Google Cloud SDK（gcloud）のインストール
1. BigQuery API を有効化する
1. Google が一般公開している一般公開データセットをプロジェクトに追加したい場合は、以下のコマンドでサイトにアクセスする<br>
    ```sh
    $ open https://console.cloud.google.com/bigquery?p=bigquery-public-data&page=project
    ```

## ■ データセットを作成する

- 空のデータセットを作成する<br>
    ```sh
    $ bq mk ${PROJECT_ID}:${DATASET_ID}
    ```
    - `${PROJECT_ID}` : データセットを作成するプロジェクトID
    - `${DATASET_ID}` : データセットID    

- データセットにテーブルデータをアップロードする（スキーマ自動定義使用）<br>
    ```sh
    $ bq load --autodetect --source_format=CSV \
        ${PROJECT_ID}:${DATASET_ID}.${TABLE_ID} \
        ${TABLE_FILE}
    ```
    - `--autodetect` : スキーマを自動的する場合に指定
    - `--source_format` : テーブルデータのフォーマット（`CSV` or `NEWLINE_DELIMITED_JSON` が使用可能） 
    - `${TABLE_FILE}` : アップロードするテーブルデータのファイルパス

- データセットにテーブルデータをアップロードする（スキーマ自動定義非使用）<br>
    ```sh
    $ bq load --source_format=CSV \
        ${PROJECT_ID}:${DATASET_ID}.${TABLE_ID} \
        ${TABLE_FILE} \
        ${SCHEMA} 
    ```
    - `${SCHEMA} ` : スキーマ定義

- データセットを確認する<br>
    ```sh
    $ bq ls ${PROJECT_ID}:
    ```

- データセットを削除する<br>
    ```sh
    $ bq rm -r -f ${DATASET_ID}
    ```
    - `-r` : データセットとテーブルをまとめて削除
    - `-f` : 強制削除オプション

## ■ テーブルデータを確認する

- テーブルデータを確認する<br>
    ```sh
    bq show ${PROJECT_ID}:${DATASET_ID}.${TABLE_ID}
    ```

- テーブルデータを確認する（一般公開データセット）<br>
    例えば、一般公開データセット（PROJECT_ID=`bigquery-public-data`）の `usa_names` データセットの `usa_1910_2013` テーブルを確認する場合は、以下のようなコマンドとなる
    ```sh
    bq show bigquery-public-data:usa_names.usa_1910_2013
    ```

## ■ クエリ（処理要求）を実行する

- クエリを実行する<br>
    ```sh
    # 構文
    $ bq query --use_legacy_sql=false "SQL_STATEMENT"
    ```
    - `--use_legacy_sql` : false に設定した場合は、標準 SQL クエリを使用。デフォルト値は true

    ```sh
    # 例 : テーブルデータの全表示
    $ bq query --use_legacy_sql=false "SELECT * FROM ${PROJECT_ID}.${DATASET_ID}.${TABLE_ID}"
    ```

- クエリを実行する（一般公開データセット）<br>
    例えば、一般公開データセット（PROJECT_ID=`bigquery-public-data`）の `usa_names` データセットの `usa_1910_2013` テーブルに対してクエリを実行する場合は、以下のようなコマンドとなる
    ```sh
    # 例 : 一般公開データセットに対して、クエリ実行
    $ bq query --use_legacy_sql=false \
        'SELECT
            name, gender,
            SUM(number) AS total
        FROM
            `bigquery-public-data.usa_names.usa_1910_2013`
        GROUP BY
            name, gender
        ORDER BY
            total DESC
        LIMIT
            10'
    ```
    ```sh
    Waiting on bqjob_r1d2b6f0ad65dd7c9_000001775794d45f_1 ... (1s) Current status: DONE
    +---------+--------+---------+
    |  name   | gender |  total  |
    +---------+--------+---------+
    | James   | M      | 4924235 |
    | John    | M      | 4818746 |
    | Robert  | M      | 4703680 |
    | Michael | M      | 4280040 |
    | William | M      | 3811998 |
    | Mary    | F      | 3728041 |
    | David   | M      | 3541625 |
    | Richard | M      | 2526927 |
    | Joseph  | M      | 2467298 |
    | Charles | M      | 2237170 |
    +---------+--------+---------+
    ```

## ■ 参考サイト
- https://cloud.google.com/bigquery/docs/quickstarts/quickstart-command-line?hl=ja
- https://www.apps-gcp.com/bq-command/
