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
# kfctl のインストール
#-------------------------------------
<<COMMENTOUT
mkdir ${HOME}/kubeflow
cd ${HOME}/kubeflow
curl -LO https://github.com/kubeflow/kfctl/releases/download/v1.0.1/kfctl_v1.0.1-0-gf3edb9b_darwin.tar.gz
tar zxf kfctl_v1.0.1-0-gf3edb9b_darwin.tar.gz
chmod +x kfctl
sudo mv kfctl /usr/local/bin/kfctl

# マニフェストファイルの読み込み
cd ${ROOT_DIR}
source kfctl_env.sh
COMMENTOUT

#-------------------------------------
# クラスタの構築
#-------------------------------------
#gcloud container clusters create ${CLUSTER_NAME} --num-nodes=${NUM_NODES}

#-------------------------------------
# `kfctl apply` コマンドで k8s クラスタに kubeflow をデプロイする
#-------------------------------------
# KF_DIR, CONFIG_URI は、`kfctl_env.sh` で export されている
mkdir -p ${KF_DIR}
cd ${KF_DIR}
kfctl apply -V -f ${CONFIG_URI}
cd ${ROOT_DIR}
kubectl get po --all-namespaces

#-------------------------------------
# Kubeflow の Central Dashboard にアクセス
#-------------------------------------
kubectl port-forward -n istio-system svc/istio-ingressgateway 80:80 --address 0.0.0.0
