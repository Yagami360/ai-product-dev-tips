# 【BigQuery】BigQuery を使用したデータ処理

## ■ GUI 使用時

### ◎ 事前準備（一般公開データセットを使用）
1. BigQuery API を有効化する
1. [BigQuery のウェブ UI ページ](https://console.cloud.google.com/bigquery?hl=ja&project=my-project2-303004) にアクセス<br>
1. Google が一般公開している一般公開データセットをプロジェクトに追加する<br>
    ```sh
    $ open https://console.cloud.google.com/bigquery?p=bigquery-public-data&page=project
    ```

### ◎ クエリ（処理要求）を実行する（一般公開データセット使用）
1. 「クエリを新規作成」ボタンをクリック<br>
1. 以下のクエリコード（SQL）を、エディタフィールドに貼り付け<br>
    ```sql
    SELECT
        name, gender,
        SUM(number) AS total
    FROM
        `bigquery-public-data.usa_names.usa_1910_2013`
    GROUP BY
        name, gender
    ORDER BY
        total DESC
    LIMIT
        10
    ```
1. 「実行」ボタンをクリック<br>
1. クエリの結果フィールドにクエリの実行結果が表示される<br>
    <img src="https://user-images.githubusercontent.com/25688193/106378265-b2e65700-63e6-11eb-95ee-66164f6fd17f.png" width="800">


### ◎ データセットを作成する
xxx


## ■ CLI 使用時
BigQuery の CLI での処理は、gcloud コマンドインストール時にインストールされている `bq` コマンドを用いて行うことができる。

### ◎ 事前準備（一般公開データセットを使用）

1. Google Cloud SDK（gcloud）のインストール
1. BigQuery API を有効化する
1. Google が一般公開している一般公開データセットをプロジェクトに追加する<br>
    ```sh
    $ open https://console.cloud.google.com/bigquery?p=bigquery-public-data&page=project
    ```

### ◎ クエリ（処理要求）を実行する（一般公開データセット使用）

1. クエリを実行する
    ```sh
    # 構文
    $ bq query "SQL_STATEMENT"
    ```
    - `--use_legacy_sql` : false に設定した場合は、標準 SQL クエリを使用。デフォルト値は true

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

### ◎ データセットを作成する
xxx

## ■ 参考サイト
- https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui?hl=ja&_ga=2.65098990.-1151485257.1612079281
- https://cloud.google.com/bigquery/docs/quickstarts/quickstart-command-line?hl=ja
- https://www.apps-gcp.com/bq-command/