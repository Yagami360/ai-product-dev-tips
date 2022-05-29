#!/bin/sh
set -eu
HOST=127.0.0.1
PORT=3306

#-----------------------------
# OS判定
#-----------------------------
if [ "$(uname)" = 'Darwin' ]; then
  OS='Mac'
  echo "Your platform is Mac."  
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

#-----------------------------------------------
# MySQL をインストールする
#-----------------------------------------------
mysql --version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        brew install mysql
    elif [ ${OS} = "Linux" ] ; then
        sudo apt install mysql-server
    fi
fi
echo "mysql --version : `mysql --version`"

#-----------------------------------------------
# SQL インスタンスへ接続する
#-----------------------------------------------
mysql -u root -p --host ${HOST} --port ${PORT}
