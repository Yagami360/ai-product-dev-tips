#!/bin/sh
set -eux

WORKDIR=${WORKDIR:-"/app"}
IMAGE_NAME=${IMAGE_NAME:-"llm-exercises"}
TAG=${TAG:-"latest"}
PROJECT_DIR=${PWD}

EPOCHS=5
BATCH_SIZE=4
SAVE_STEP=1000

# -------------------
# Build Docker Image
# -------------------
if ! docker images ${IMAGE_NAME}:${TAG} | grep -q ${IMAGE_NAME}; then
    echo "Building Docker image ${IMAGE_NAME}:${TAG}..."
    docker build -t ${IMAGE_NAME}:${TAG} -f Dockerfile .
else
    echo "Docker image ${IMAGE_NAME}:${TAG} already exists."
fi

docker run --rm --gpus all -v ${PROJECT_DIR}:${WORKDIR} \
    ${IMAGE_NAME}:${TAG} /bin/bash -c \
        "python3 train.py \
        --epochs ${EPOCHS} \
        --batch_size ${BATCH_SIZE} \
        --save_step ${SAVE_STEP} \
        "
