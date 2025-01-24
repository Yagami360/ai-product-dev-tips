#!/bin/sh
set -eu

sudo apt update

# intall rke
wget https://github.com/rancher/rke/releases/latest/download/rke_linux-amd64
mv rke_linux-amd64 rke
chmod +x rke

# add rke cluster setting
cat > cluster.yml <<EOL
nodes:
- address: [サーバーIP]
    user: [SSHユーザー名]
    role: [controlplane,etcd,worker]
EOL

# start rke cluster
./rke up
