#!/bin/sh
set -eu
PROXY_HOST=localhost
PROXY_PORT=8080

API_SERVER1_HOST=localhost
API_SERVER1_PORT=5000

API_SERVER2_HOST=localhost
API_SERVER2_PORT=5001

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
#docker-compose logs --tail=10

# Nginx の Web サーバーにブラウザアクセス
set +e
echo "requst to proxy server"
curl http://${PROXY_HOST}:${PROXY_PORT}               # nginx プロキシサーバにアクセス

echo "requst to web server1"
curl http://${API_SERVER1_HOST}:${API_SERVER1_PORT}   # uWSGI 経由で Flask-API サーバー１にアクセス

echo "requst to web server2"
curl http://${API_SERVER2_HOST}:${API_SERVER2_PORT}   # uWSGI 経由で Flask-API サーバー２にアクセス
set -e

docker-compose logs --tail=10

#<<COMMENTOUT
if [ ${OS} = 'Mac' ]; then
    open http://${PROXY_HOST}:${PROXY_PORT}               # nginx プロキシサーバにアクセス
    open http://${API_SERVER1_HOST}:${API_SERVER1_PORT}   # uWSGI 経由で Flask-API サーバー１にアクセス
    open http://${API_SERVER2_HOST}:${API_SERVER2_PORT}   # uWSGI 経由で Flask-API サーバー２にアクセス
fi
#COMMENTOUT