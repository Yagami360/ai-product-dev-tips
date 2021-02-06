# 【BigQuery】BigQuery を使用したデータ処理（Python 用 BigQuery Storage API ライブラリ使用時）
Python 用 BigQuery Storage API ライブラリを使用することで、Python コードから BigQuery にアクセスすることができる。<br>
Python から BigQuery にアクセスするためのライブラリには主に、以下の２種類が存在する

- Google SDK の `google-cloud-bigquery`, `google-cloud-bigquery-storage`
- pandas の `pandas.io.gbq`
    - こちらのほうが手軽に使用可能

## ■ `google-cloud-bigquery`, `google-cloud-bigquery-storage` を使用する場合

### ◎ 事前準備
- Python 用 BigQuery Storage API クライアントライブラリのインストール
    ```sh
    # pip 使用時

    ```

    ```sh
    # conda 使用時
    ```

### ◎ データセットを作成する
xxx

### ◎ クエリ（処理要求）を実行する
xxx

## ■ `pandas.io.gbq` を使用する場合
xxx

## ■ 参考サイト
- https://cloud.google.com/bigquery/docs/bigquery-storage-python-pandas?hl=ja
- https://qiita.com/Hyperion13fleet/items/0e00f4070f623dacf92b
- https://qiita.com/hik0107/items/3944ccea04371331c3b4