IMAGE_NAME=python_image
CONTAINER_NAME=python_container
if [ ! "$(docker image ls -q ${IMAGE_NAME})" ]; then
    docker build ./ -t ${IMAGE_NAME}
fi

docker run -it --rm --name ${CONTAINER_NAME} \
    -v ${PWD}:/workspace \
    ${IMAGE_NAME} /bin/bash
