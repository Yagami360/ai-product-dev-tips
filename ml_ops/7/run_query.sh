#!/bin/sh
set -eu

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

