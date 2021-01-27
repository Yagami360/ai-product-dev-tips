#!/bin/sh
set -eu

PROJECT_ID="my-project2-303004"
cd pipelines

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config list

# Kubeflow Pipelines SDK のインストール
#pip install kfp

# docker image を GCP の Container Registry にアップロード
#gcloud builds submit --config cloudbuild.yml

# pipleline 用 yaml ファイルの作成
python pipeline.py

# yaml ファイルのアップロード
# [Todo] gcloud などのコマンドで自動化したい

# pipleline 上で動作している Pod にアクセス
#POD_NAME=download-dataset-pipeline-7jmgb-2036900286
#kubectl exec -it ${POD_NAME} /bin/bash
