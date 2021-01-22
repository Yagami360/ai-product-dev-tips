#!/bin/sh
set -eu

ROOT_DIR=${PWD}
PROJECT_ID=myproject-292103
CLIENT_ID=378574289136-l3vl0c4ev2vrl58tuqgddm7rm9jdk467.apps.googleusercontent.com
CLIENT_SECRET=rozdWJfh1tnzYoU6nv5QvJot

#REGION=asia-northeast1-a
#REGION=asia-northeast1-c
#REGION=us-central1-a
#REGION=us-central1-c
REGION=asia-east1-a
CPU_TYPE=n1-standard-4

if [ ${REGION} = "asia-east1-a" ] ; then
    GPU_TYPE=nvidia-tesla-k80
elif [ ${REGION} = "us-central1-a" ] ; then
    GPU_TYPE=nvidia-tesla-k80
elif [ ${REGION} = "us-central1-c" ] ; then
    GPU_TYPE=nvidia-tesla-k80
else
    GPU_TYPE=nvidia-tesla-t4
fi

CLUSTER_NAME=kubeflow-cluster
SERVICE_NAME=kubeflow-server
NUM_NODES=1
POD_NAME=kubeflow-pod
PORT=80

# ログイン
#gcloud auth login
#gcloud auth application-default login

# デフォルト値の設定
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${REGION}
gcloud config list

#-------------------------------------
# kfctl のインストール
#-------------------------------------
#<<COMMENTOUT
mkdir -p kubeflow
cd kubeflow
#curl -LO https://github.com/kubeflow/kfctl/releases/download/v1.0.1/kfctl_v1.0.1-0-gf3edb9b_darwin.tar.gz
#tar zxf kfctl_v1.0.1-0-gf3edb9b_darwin.tar.gz
curl -LO https://github.com/kubeflow/kfctl/releases/download/v1.0.2/kfctl_v1.0.2-0-ga476281_darwin.tar.gz
tar zxf kfctl_v1.0.2-0-ga476281_darwin.tar.gz
chmod +x kfctl
sudo mv kfctl /usr/local/bin/kfctl
cd ${ROOT_DIR}
#COMMENTOUT

#-------------------------------------
# kfctl 用環境変数の設定
#-------------------------------------
export BASE_DIR=${ROOT_DIR}/kubeflow
export PATH=${PATH}:${BASE_DIR}
export KF_NAME=${CLUSTER_NAME}
export KF_DIR=${BASE_DIR}/${KF_NAME}
#export CONFIG_URI="https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_gcp_iap.v1.0.0.yaml"
export CONFIG_URI="https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_gcp_iap.v1.0.2.yaml"
export CLIENT_ID=${CLIENT_ID}
export CLIENT_SECRET=${CLIENT_SECRET}

#-------------------------------------
# クラスタの構築
#-------------------------------------
#<<COMMENTOUT
gcloud container clusters create ${CLUSTER_NAME} \
    --machine-type=${CPU_TYPE} \
    --accelerator type=${GPU_TYPE},count=1 \
    --num-nodes=${NUM_NODES}
#COMMENTOUT

#-------------------------------------
# `kfctl apply` コマンドで k8s クラスタに kubeflow をデプロイする
#-------------------------------------
rm -rf ${KF_DIR}
mkdir -p ${KF_DIR}
cd ${KF_DIR}
kfctl apply -V -f ${CONFIG_URI}
cd ${ROOT_DIR}

#-------------------------------------
# デプロイした kubeflow の Pod と Service が正常に起動しているか確認する
#-------------------------------------
sleep 30
kubectl get pod --all-namespaces
kubectl get services --all-namespaces

#-------------------------------------
# Kubeflow の Central Dashboard にアクセス
#-------------------------------------
kubectl port-forward -n istio-system svc/istio-ingressgateway 80:80 --address 0.0.0.0
#https://${KF_NAME}.endpoints.${PROJECT_ID}.cloud.goog/