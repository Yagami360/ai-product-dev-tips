#!/bin/sh
set -eu
PROJECT_ID=bigquery-public-data
DATASET_ID=usa_names
TABLE_ID=usa_1910_2013

bq show ${PROJECT_ID}:${DATASET_ID}.${TABLE_ID}

bq query --use_legacy_sql=false \
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

