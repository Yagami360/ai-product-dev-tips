#!/bin/sh
set -eu

SERVER_EXTERNAL_IP="xxx.xxx.xxx.xxx"
SERVER_INTERNAL_IP="xxx.xxx.xxx.xxx"
SSH_USER="ubuntu"

sudo apt update

# intall rke
wget https://github.com/rancher/rke/releases/latest/download/rke_linux-amd64
mv rke_linux-amd64 rke
chmod +x rke

# add rke cluster setting
cat > cluster.yml <<EOL
nodes:
- address: ${SERVER_EXTERNAL_IP}
  internal_address: ${SERVER_INTERNAL_IP}
  user: ${SSH_USER}
  role: [controlplane,etcd,worker]
  ssh_key_path: ~/.ssh/id_rsa
EOL

# deploy rke cluster
./rke up

# copy kubeconfig
# cp kube_config_cluster.yml ~/.kube/config
cp ~/.kube/config ~/.kube/config.bak
KUBECONFIG=~/.kube/config:kube_config_cluster.yml kubectl config view --flatten > ~/.kube/config.new
mv ~/.kube/config.new ~/.kube/config

# check cluster status
kubectl --kubeconfig=kube_config_cluster.yml get nodes

# deploy nginx pod
kubectl --kubeconfig=kube_config_cluster.yml apply -f k8s/nginx.yaml

# check nginx pod
kubectl --kubeconfig=kube_config_cluster.yml get pods
