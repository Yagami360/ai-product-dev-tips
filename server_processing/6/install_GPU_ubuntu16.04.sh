#!/bin/sh
set -eu

# install GCP Cloud SDK

# install GPU driver (NVIDIA Tesla T4) and CUDA
curl -O http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_9.0.176-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1604_9.0.176-1_amd64.deb
sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/7fa2af80.pub
sudo apt-get update
sudo apt-get install cuda-9-0
rm -rf cuda-repo-ubuntu1604_9.0.176-1_amd64.deb

# optimize GPU
sudo nvidia-smi -pm 1
sudo nvidia-smi --auto-boost-default=DISABLED

# install cuDNN
# 事前に https://developer.nvidia.com/rdp/cudnn-download から、"libcudnn7_7.6.5.32-1+cuda9.0_amd64.deb", "libcudnn7-dev_7.6.5.32-1+cuda9.0_amd64.deb", "libcudnn7-doc_7.6.5.32-1+cuda9.0_amd64.deb" をダウンロードする必要あり（認証付き）
# 以下の curl コマンドは、事前に GCP ストレージ上に保存したファイルからダウンロードしている。
curl -O https://storage.cloud.google.com/storage_360/libcudnn7-dev_7.6.5.32-1%2Bcuda9.0_amd64.deb?hl=ja
curl -O https://storage.cloud.google.com/storage_360/libcudnn7-doc_7.6.5.32-1%2Bcuda9.0_amd64.deb?hl=ja
curl -O https://storage.cloud.google.com/storage_360/libcudnn7_7.6.5.32-1%2Bcuda9.0_amd64.deb?hl=ja

sudo dpkg -i libcudnn7_7.6.5.32-1+cuda9.0_amd64.deb
sudo dpkg -i libcudnn7-dev_7.6.5.32-1+cuda9.0_amd64.deb
sudo dpkg -i libcudnn7-doc_7.6.5.32-1+cuda9.0_amd64.deb
rm -rf libcudnn7_7.6.5.32-1+cuda9.0_amd64.deb
rm -rf libcudnn7-dev_7.6.5.32-1+cuda9.0_amd64.deb
rm -rf libcudnn7-doc_7.6.5.32-1+cuda9.0_amd64.deb

# install basic
sudo apt-get install zip unzip

# install pip
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip
pip3 install --upgrade pip

# install conda
wget https://repo.anaconda.com/archive/Anaconda3-2019.03-Linux-x86_64.sh
bash Anaconda3-2019.03-Linux-x86_64.sh
source ~/.bashrc
conda -V
conda update -n base -c defaults conda
rm -rf Anaconda3-2019.03-Linux-x86_64.sh

# install Docker
