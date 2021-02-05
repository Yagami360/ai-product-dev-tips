#!/bin/sh
set -eu

PROJECT_ID=my-project2-303004
DATASET_ID=sample_dataset
TABLE_ID=sample_table
TABLE_FILE="datasets/1.csv"

# データセットの削除
bq rm -r -f ${DATASET_ID}

# 空のデータセットを作成する
bq mk ${PROJECT_ID}:${DATASET_ID}
bq ls ${PROJECT_ID}:

# 空のデータセットにテーブルデータを追加する
bq load --autodetect --source_format=CSV \
    ${PROJECT_ID}:${DATASET_ID}.${TABLE_ID} \
    ${TABLE_FILE} 

# テーブルデータを確認する
bq show ${PROJECT_ID}:${DATASET_ID}.${TABLE_ID}

# クエリ（処理要求）を実行する / テーブルデータの全表示
bq query --use_legacy_sql=false "SELECT * FROM ${PROJECT_ID}.${DATASET_ID}.${TABLE_ID}"
