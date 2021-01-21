#!/bin/sh
set -eu

ROOT_DIR=${PWD}
PROJECT_ID=myproject-292103
REGION=asia-northeast1-a
CLUSTER_NAME=kubeflow-cluster
SERVICE_NAME=kubeflow-server
NUM_NODES=1
POD_NAME=kubeflow-pod
PORT=80

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${REGION}
gcloud config list

#-------------------------------------
# ksonnet インストール
#-------------------------------------
brew install ksonnet/tap/ks

#-------------------------------------
# クラスタの構築
#-------------------------------------
gcloud container clusters create ${CLUSTER_NAME} --num-nodes=${NUM_NODES}

#-------------------------------------
# ksonnet コマンド `ks` で kubeflow をデプロイする
#-------------------------------------
#<<COMMENTOUT
# kubeflow という初期設定済のディレクトリ作成
ks init kubeflow
cd kubeflow

# kubeflow のリポジトリを登録
ks registry add kubeflow github.com/google/kubeflow/tree/master/kubeflow
ks pkg install kubeflow/core
ks pkg install kubeflow/tf-serving
ks pkg install kubeflow/tf-job
ks generate core kubeflow-core --name=kubeflow-core  

# ksonnet に GKE 環境を追加
CONTENT_NAME=`kubectl config current-context`
kubectl config use-context ${CONTENT_NAME}
ks env add kubeflow_gke
#COMMENTOUT
