#!/bin/sh
set -eu

PROJECT_ID=my-project2-303004
SINK_NAME=export-logs-to-datadog-sink
TOPIC_NAME=export-logs-to-datadog

# シンク作成権限のある個人アカウントに変更
#gcloud auth login

# API を有効化する

# ClloudLogging の「ログルータ」からシンクを作成する
gcloud logging sinks create \
    ${SINK_NAME} \
    pubsub.googleapis.com/projects/${PROJECT_ID}/topics/${TOPIC_NAME}

gcloud logging sinks list

