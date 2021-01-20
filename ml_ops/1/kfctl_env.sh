#!/bin/sh
#source install_kfctl.sh
set -eu
export BASE_DIR=${HOME}/kubeflow
export PATH=${PATH}:${BASE_DIR}
export KF_NAME=mykubeflow
export KF_DIR=${BASE_DIR}/${KF_NAME}
export CONFIG_URI="https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_k8s_istio.v1.0.1.yaml"