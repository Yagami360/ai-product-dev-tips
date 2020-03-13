#-----------------------------
# Docker イメージのベースイメージ
#-----------------------------
# CUDA 10.0 for Ubuntu 16.04
FROM nvidia/cuda:10.0-base-ubuntu16.04

#-----------------------------
# 基本ライブラリのインストール
#-----------------------------
ENV DEBIAN_FRONTEND noninteractive
RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    git \
    curl \
    wget \
    bzip2 \
    ca-certificates \
    libx11-6 \
    python3-pip \
    # imageのサイズを小さくするためにキャッシュ削除
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#-----------------------------
# 環境変数
#-----------------------------
ENV LC_ALL=C.UTF-8
ENV export LANG=C.UTF-8
ENV PYTHONIOENCODING utf-8

ARG WORK_DIR=/workspace

#-----------------------------
# ユーザーの追加
#-----------------------------

#-----------------------------
# 追加ライブラリのインストール
#-----------------------------
RUN pip3 install tqdm
RUN pip3 install pillow==6.2.1

#-----------------------------
# コンテナ起動後に自動的に実行するコマンド
#-----------------------------

#-----------------------------
# コンテナ起動後の作業ディレクトリ
#-----------------------------
# 作業ディレクトリを / 直下の `/workspace` にする
# これにより、コンテナ内のユーザーが root ユーザーになる。
WORKDIR ${WORK_DIR}
