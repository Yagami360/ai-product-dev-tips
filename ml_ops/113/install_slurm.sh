#!/bin/sh
set -eu
PROJECT_DIR=$(cd $(dirname $0)/..; pwd)
SLURM_VERSION=22.05.8

lsb_release -a

sudo apt update

# Install MUNGE
# MUNGE: HPC [High Performance Computing] 環境でよく使用されるライブラリで、Slurm などでのノード間通信を安全に行うための認証を提供する
sudo apt install -y munge
sudo apt install -y libmunge-dev

# MUNGE を起動する
sudo systemctl enable munge
sudo systemctl start munge

# MUNGE の起動状態を確認する
sudo systemctl status munge

# Install gcc
# SLURM をビルドする際に必要になるため、gcc をインストールする
sudo apt install -y gcc

# -------------------
# Install SLURM
# -------------------
# download SLURM
cd ${HOME}
wget https://download.schedmd.com/slurm/slurm-${SLURM_VERSION}.tar.bz2
tar xvjf slurm-${SLURM_VERSION}.tar.bz2
sudo rm -rf slurm-${SLURM_VERSION}.tar.bz2
cd ${HOME}/slurm-${SLURM_VERSION}

# Build SLURM
./configure --with-munge
make
sudo make install

# check munge is running
grep -i munge config.log

# -------------------
# Setup SLURM
# -------------------
sudo cp etc/slurm.conf.example /usr/local/etc/slurm.conf

# -------------------
# Run SLURM
# -------------------
# 
sudo cp etc/slurmctld.service /etc/systemd/system
sudo cp etc/slurmd.service /etc/systemd/system

# start slurmctld and slurmd
sudo systemctl start slurmctld slurmd

# check slurm is running
sudo systemctl status slurmctld slurmd
