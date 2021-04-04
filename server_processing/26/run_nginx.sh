#!/bin/sh
set -eu
PROXY_IMAGE_NAME=nginx-proxy-image
PROXY_CONTAINER_NAME=nginx-proxy-container
PROXY_HOST=localhost
PROXY_PORT=8080
AUTO_EXEC=0

docker build proxy -t ${PROXY_IMAGE_NAME}
if [ ${AUTO_EXEC} = 1 ] ; then
    docker run -it -d --rm -v ${PWD}/proxy:/proxy -p ${PROXY_PORT}:${PROXY_PORT} --name ${PROXY_CONTAINER_NAME} ${PROXY_IMAGE_NAME}
    docker exec -it ${PROXY_CONTAINER_NAME} /bin/bash -c "sudo nginx -c /proxy/nginx/proxy.conf"
    docker logs ${PROXY_CONTAINER_NAME}
else
    docker run -it --rm -v ${PWD}/proxy:/proxy -p ${PROXY_PORT}:${PROXY_PORT} --name ${PROXY_CONTAINER_NAME} ${PROXY_IMAGE_NAME} /bin/bash
fi
