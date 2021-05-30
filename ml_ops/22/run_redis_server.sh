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

# Redis のインストール
if [ ${OS} = "Mac" ] ; then
    brew install redis
elif [ ${OS} = "Linux" ] ; then
    sudo apt install redis-server
fi

redis-cli --version
redis-server --version

# Redis サーバーを起動する
redis-server
