#FROM alpine:3.10
FROM python:3.8-slim

# Install basic
ENV DEBIAN_FRONTEND noninteractive
RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    wget \
    unzip \
    curl \
    python3-pip \
    # imageのサイズを小さくするためにキャッシュ削除
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

# Install terraform
#ARG terraform_version="0.12.5"
ARG terraform_version="1.2.3"
RUN wget https://releases.hashicorp.com/terraform/${terraform_version}/terraform_${terraform_version}_linux_amd64.zip \
    && unzip ./terraform_${terraform_version}_linux_amd64.zip -d /usr/local/bin/ \
    && rm -rf ./terraform_${terraform_version}_linux_amd64.zip

# install gcloud
RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz
RUN mkdir -p /usr/local/gcloud \
  && tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz \
  && /usr/local/gcloud/google-cloud-sdk/install.sh
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

# コンテナ起動後の作業ディレクトリ
WORKDIR /.config/gcloud
WORKDIR /terraform
