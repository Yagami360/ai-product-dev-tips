#!/bin/sh
set -eu

# delete all pods
kubectl delete pods --all --all-namespaces

# remove rke cluster
./rke remove

# remove kubeconfig
rm -rf kube_config_cluster.yml
