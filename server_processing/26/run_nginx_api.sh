#!/bin/sh
set -eu
PROXY_CONTAINER_NAME=nginx-proxy-container
PROXY_HOST=localhost
PROXY_PORT=8080

SERVER1_CONTAINER_NAME=flask-api-container
SERVER1_HOST=localhost
#SERVER1_HOST=104.196.244.26
SERVER1_PORT=5000

SERVER2_CONTAINER_NAME=flask-api-container2
SERVER2_HOST=localhost
#SERVER2_HOST=104.196.244.26
SERVER2_PORT=5001

# OS 判定
if [ "$(uname)" = 'Darwin' ]; then
  OS='Mac'
  echo "Your platform is MacOS."  
elif [ "$(expr substr $(uname -s) 1 5)" = 'Linux' ]; then
  OS='Linux'
  echo "Your platform is Linux."  
elif [ "$(expr substr $(uname -s) 1 10)" = 'MINGW32_NT' ]; then                                                                                           
  OS='Cygwin'
  echo "Your platform is Cygwin."  
else
  echo "Your platform ($(uname -a)) is not supported."
  exit 1
fi

# コンテナ起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d

docker logs ${PROXY_CONTAINER_NAME}
#docker logs ${SERVER1_CONTAINER_NAME}
#docker logs ${SERVER2_CONTAINER_NAME}

# Nginx の Web サーバーにブラウザアクセス
set +e
echo "requst to proxy server"
curl http://${PROXY_HOST}:${PROXY_PORT}       # nginx プロキシサーバにアクセス

echo "requst to web server1"
curl http://${SERVER1_HOST}:${SERVER1_PORT}   # Flask-API サーバー１にアクセス

echo "requst to web server2"
curl http://${SERVER2_HOST}:${SERVER2_PORT}   # Flask-API サーバー２にアクセス
set -e

<<COMMENTOUT
if [ ${OS} = 'Mac' ]; then
    open http://${PROXY_HOST}:${PROXY_PORT}       # nginx プロキシサーバにアクセス
    open http://${SERVER1_HOST}:${SERVER1_PORT}   # Flask-API サーバー１にアクセス
    open http://${SERVER2_HOST}:${SERVER2_PORT}   # Flask-API サーバー２にアクセス
fi
COMMENTOUT
