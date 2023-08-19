FROM python:3.9-buster

# install basic libs
ENV DEBIAN_FRONTEND noninteractive

RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    sudo \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

# define ARG and ENV
ARG WORKDIR="/app"
ENV WORKDIR=${WORKDIR}

ENV LC_ALL=C.UTF-8
ENV export LANG=C.UTF-8
ENV PYTHONIOENCODING utf-8

# install dependences
WORKDIR ${WORKDIR}
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# write src
COPY . ${WORKDIR}

# set workdir
WORKDIR ${WORKDIR}
