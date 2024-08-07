#!/bin/sh
set -eu
NGINX_CONF_FILE_PATH="${PWD}/nginx/nginx.conf"
#NGINX_CONF_FILE_PATH="${PWD}/nginx/nginx_default.conf"
PORT=80
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

# Nginx の Web サーバーを起動
sudo nginx -c ${NGINX_CONF_FILE_PATH}
#sudo nginx -s reload

# Nginx の Web サーバーにブラウザアクセス
curl http://localhost:${PORT}
if [ ${OS} = 'Mac' ]; then
    sleep 1
    open http://localhost:${PORT}
fi
