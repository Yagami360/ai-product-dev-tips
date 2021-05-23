#!/bin/sh
set -eu
DOCKER_FILE_NAME="Dockerfile_pytorch18_cuda102"
IMAGE_NAME=pytorch18-cuda102-image
CONTAINER_NAME=pytorch18-cuda102-container
PORT=6006

if [ ! "$(docker image ls -q ${IMAGE_NAME})" ]; then
    docker build -f ${DOCKER_FILE_NAME} . -t ${IMAGE_NAME}
fi

if [ "$(docker ps | grep ${CONTAINER_NAME})" ]; then
    docker rm -f ${CONTAINER_NAME}
fi

cd ..
docker run -it --rm -v ${PWD}:"/MachineLearning_Tips" -p ${PORT}:${PORT} --gpus all --shm-size=16gb --name ${CONTAINER_NAME} ${IMAGE_NAME}
