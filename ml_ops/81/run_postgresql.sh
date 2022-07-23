#!/bin/sh
set -eu

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
# PostgreSQL
#=============================
mkdir -p postgresql

# PostgreSQL サーバー起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# PostgreSQL サーバーに接続する
docker exec -it postgresql-container /bin/bash -c "psql -h localhost -U postgres"