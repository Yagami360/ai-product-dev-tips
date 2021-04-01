#!/bin/sh
set -eu

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

# nginx 停止
#sudo nginx -s quit

# Nginx の Web サーバーを起動
sudo nginx
sudo nginx -s reload

# Nginx の Web サーバーにブラウザアクセス
if [ ${OS} = 'Mac' ]; then
    sleep 1
    open https://localhost:8080
fi
