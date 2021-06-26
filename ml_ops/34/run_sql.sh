#!/bin/sh
set -eu
INIT_ROOT_USER=0
#INIT_ROOT_USER=1

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

# MySQL をインストールする
if [ ${OS} = 'Mac' ] ; then
    brew install mysql
fi
mysql --version

# MySQL サーバーの root ユーザーを作成する
if [ ! ${INIT_ROOT_USER} = 0 ] ; then
  mysql_secure_installation
fi

# PyMySQL をインストールする
if [ ! "$(pip list | grep PyMySQL)" ] ; then
    pip install PyMySQL
fi 

# SQLAlchemy をインストールする
if [ ! "$(pip list | grep SQLAlchemy)" ] ; then
    pip install sqlalchemy
fi

# MySQL サーバーの停止
mysql.server stop

# MySQL サーバーの起動
mysql.server start

# Python スクリプトの実行
python crud.py --debug

# MySQL サーバーの停止
mysql.server stop
