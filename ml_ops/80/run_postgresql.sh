#!/bin/sh
#set -eu

#=============================
# OS判定
#=============================
if [ "$(uname)" = 'Darwin' ] ; then
    OS='Mac'
    echo "Your platform is MacOS."  
elif [ "$(expr substr $(uname -s) 1 5)" = 'Linux' ] ; then
    OS='Linux'
    echo "Your platform is Linux."  
elif [ "$(expr substr $(uname -s) 1 10)" = 'MINGW32_NT' ] ; then                                                                                           
    OS='Cygwin'
    echo "Your platform is Cygwin."  
else
    echo "Your platform ($(uname -a)) is not supported."
    exit 1
fi

#=============================
# PostgreSQL CLI のインストール
#=============================
psql --version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        brew update
        brew install postgresql
    elif [ ${OS} = "Linux" ] ; then
        sudo apt install -y postgresql-client
    fi
fi

echo "psql version : `psql --version`"

#=============================
# PostgreSQL CLI を使用して
#=============================
# PostgreSQL サーバーを起動する
if [ ${OS} = "Mac" ] ; then
    brew services stop postgresql
    brew services start postgresql
    sleep 1
fi

# PostgreSQL サーバーに接続する
psql postgres
