# FROM nvidia/cuda:11.2.2-cudnn8-runtime-ubuntu20.04
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

# install basic libs
ENV DEBIAN_FRONTEND noninteractive

RUN apt update && apt upgrade -y && \
    apt install -y wget curl && \
    apt install --no-install-recommends -y \
    git make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
    jq

# define ARG and ENV
ARG WORKDIR="/app"
ENV WORKDIR=${WORKDIR}

# Install Python
RUN apt install --no-install-recommends -y python3 python3-pip python3-setuptools
RUN pip3 install --upgrade pip

# Install PyTorch
RUN pip3 install torch==1.12.0+cpu torchvision==0.13.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu
# RUN pip3 install torch==1.12.0+cu113 torchvision==0.13.0+cu113 --extra-index-url https://download.pytorch.org/whl/cu113

# Install TensorFlow
RUN pip3 install tensorflow

# Downgrade to avoid the error in Transformers
RUN pip3 install protobuf==3.20.0
RUN pip3 install accelerate>=0.26.0

# Install HuggingFace Transformers
RUN pip3 install transformers
RUN pip3 install datasets

# Install Other dependences
WORKDIR ${WORKDIR}
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# write src
COPY . ${WORKDIR}

# set workdir
WORKDIR ${WORKDIR}

# config & cleanup
RUN apt purge -y build-essential

RUN ldconfig && \
    apt-get -y clean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/*
