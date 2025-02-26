#!/bin/sh
set -eux

WORKDIR=${WORKDIR:-"/app"}
IMAGE_NAME=${IMAGE_NAME:-"llm-exercises"}
TAG=${TAG:-"latest"}
PROJECT_DIR=${PWD}

# MODEL_NAME=${MODEL_NAME:-"gpt2"}
MODEL_NAME=${MODEL_NAME:-"Qwen/Qwen-7B"}
EPOCHS=10
BATCH_SIZE=4
SAVE_STEP=1000

# -------------------
# Build Docker Image
# -------------------
# set +x
# docker rmi ${IMAGE_NAME}:${TAG}
# set -x
if ! docker images ${IMAGE_NAME}:${TAG} | grep -q ${IMAGE_NAME}; then
    echo "Building Docker image ${IMAGE_NAME}:${TAG}..."
    docker build -t ${IMAGE_NAME}:${TAG} -f Dockerfile .
else
    echo "Docker image ${IMAGE_NAME}:${TAG} already exists."
fi

sudo rm -rf .results
docker run --rm -v ${PROJECT_DIR}:${WORKDIR} \
    ${IMAGE_NAME}:${TAG} /bin/bash -c \
        "python3 train.py \
        --model_name ${MODEL_NAME} \
        --epochs ${EPOCHS} \
        --batch_size ${BATCH_SIZE} \
        --save_step ${SAVE_STEP} \
        "
