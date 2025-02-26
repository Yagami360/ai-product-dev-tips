#!/bin/sh
set -eux

WORKDIR=${WORKDIR:-"/app"}
IMAGE_NAME=${IMAGE_NAME:-"llm-exercises"}
TAG=${TAG:-"latest"}
PROJECT_DIR=${PWD}

# -------------------
# Build Docker Image
# -------------------
set +eu
docker rmi ${IMAGE_NAME}:${TAG}
set -eu
if ! docker images ${IMAGE_NAME}:${TAG} | grep -q ${IMAGE_NAME}; then
    echo "Building Docker image ${IMAGE_NAME}:${TAG}..."
    docker build -t ${IMAGE_NAME}:${TAG} -f Dockerfile .
else
    echo "Docker image ${IMAGE_NAME}:${TAG} already exists."
fi

sudo rm -rf .results
docker run --rm -v ${PROJECT_DIR}:${WORKDIR} \
    ${IMAGE_NAME}:${TAG} /bin/bash -c \
        "python3 predict.py
        "