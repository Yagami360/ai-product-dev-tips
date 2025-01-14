#!/bin/sh
set -eu
PROXY_CONF_FILE_PATH="${PWD}/nginx/proxy.conf"
PROXY_HOST=localhost
PROXY_PORT=80

SERVER_CONF_FILE_PATH="${PWD}/nginx/server.conf"
SERVER_HOST=localhost
SERVER_PORT=8080

KILL_NGINX_PROCESS=0

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

# nginx のインストール
if [ ${OS} = 'Mac' ]; then
    brew install nginx
fi

# nginx のバージョン確認
nginx -v

# nginx プロセス確認
#ps aux | grep nginx

# nginx 停止
set +e
sudo nginx -s quit
set -e

# nginx 関連のプロセスを全て kill | sudo nginx -s quit でも停止できないときのための処理
if [ ${KILL_NGINX_PROCESS} = 1 ] ; then
    ps aux | grep [n]ginx | awk '{ print "sudo kill -9", $2 }'
    sudo pkill nginx
    sleep 5
fi

# Nginx を起動
sudo nginx -c ${PROXY_CONF_FILE_PATH}
sudo nginx -c ${SERVER_CONF_FILE_PATH}

# Nginx の Web サーバーにブラウザアクセス
set +e
curl http://${PROXY_HOST}:${PROXY_PORT}       # プロキシサーバにアクセス
curl http://${SERVER_HOST}:${SERVER_PORT}     # プロキシサーバ接続先サーバーにアクセス
set -e

if [ ${OS} = 'Mac' ]; then
    open http://${PROXY_HOST}:${PROXY_PORT}       # プロキシサーバにアクセス
    open http://${SERVER_HOST}:${SERVER_PORT}     # プロキシサーバ接続先サーバーにアクセス
fi
