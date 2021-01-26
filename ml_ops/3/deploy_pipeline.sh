#!/bin/sh
set -eu

PROJECT_ID="myproject-292103"
cd pipelines

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config list

# docker image を GCP の Container Registry にアップロード
gcloud builds submit --config cloudbuild.yml

# pipleline 用 yaml ファイルの作成
python pipeline.py

# yaml ファイルのアップロード
# [Todo] gcloud などのコマンドで自動化したい

