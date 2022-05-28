#-----------------------------
# Docker イメージのベースイメージ
#-----------------------------
FROM python:3.8-slim
#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

#-----------------------------
# 基本ライブラリのインストール
#-----------------------------
# インストール時のキー入力待ちをなくす環境変数
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

RUN pip3 install --upgrade pip

#-----------------------------
# 環境変数
#-----------------------------
ENV LC_ALL=C.UTF-8
ENV export LANG=C.UTF-8
ENV PYTHONIOENCODING utf-8

#-----------------------------
# 追加ライブラリのインストール
#-----------------------------
# miniconda のインストール
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda
    
# conda 上で Python 3.6 環境を構築
ENV CONDA_DEFAULT_ENV=py36
RUN conda create -y --name ${CONDA_DEFAULT_ENV} python=3.6.9 && conda clean -ya
ENV CONDA_PREFIX=/miniconda/envs/${CONDA_DEFAULT_ENV}
ENV PATH=${CONDA_PREFIX}/bin:${PATH}
RUN conda install conda-build=3.18.9=py36_3 && conda clean -ya

# OpenCV3 のインストール
RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    libgtk2.0-0 \
    libcanberra-gtk-module \
    && sudo rm -rf /var/lib/apt/lists/*

RUN conda install -y -c menpo opencv3=3.1.0 && conda clean -ya

# Others
RUN conda install -y tqdm && conda clean -ya
RUN conda install -y -c anaconda pillow==6.2.1 && conda clean -ya
RUN conda install -y -c anaconda requests && conda clean -ya
RUN conda install -y -c conda-forge fastapi && conda clean -ya
RUN conda install -y -c conda-forge uvicorn && conda clean -ya
RUN conda install -y -c conda-forge Gunicorn && conda clean -ya
RUN conda install -y -c conda-forge dataclasses && conda clean -ya
RUN pip3 install contextlib2

#-----------------------------
# ソースコードの書き込み
#-----------------------------
WORKDIR /api/predict-server
COPY . . 

#-----------------------------
# ポート開放
#-----------------------------

#-----------------------------
# コンテナ起動後に自動的に実行するコマンド
#-----------------------------

#-----------------------------
# コンテナ起動後の作業ディレクトリ
#-----------------------------
WORKDIR /api/predict-server