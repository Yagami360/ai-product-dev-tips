# 【Docker】 Docker イメージの作成＆コンテナ起動を一括して実行する

```sh
#!/bin/sh
set -e

IMAGE_NAME=ml_exercises_pytorch_image
CONTAINER_NAME=ml_exercises_container
HOST_DIR=${HOME}/MachineLearning_Exercises_Python_PyTorch
CONTAINER_DIR=/workspace/MachineLearning_Exercises_Python_PyTorch

if [ ! "$(docker image ls -q ${IMAGE_NAME})" ]; then
    docker build ./ -t ${IMAGE_NAME}
fi

if [ ! "$(docker ps -aqf "name=${CONTAINER_NAME}")" ]; then
    docker run -it --rm -v ${HOST_DIR}:${CONTAINER_DIR} --name ${CONTAINER_NAME} ${IMAGE_NAME} /bin/bash
else
    docker start ${CONTAINER_NAME}
    docker exec -it ${CONTAINER_NAME} /bin/bash
fi
```
