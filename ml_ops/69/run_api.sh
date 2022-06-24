#!/bin/sh
set -eu
PORT=3000

#-----------------------------
# OS判定
#-----------------------------
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

#-----------------------------
# Go lang のインストール
#-----------------------------
go version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        brew install go
    elif [ ${OS} = "Linux" ] ; then
        wget https://dl.google.com/go/go1.13.5.linux-amd64.tar.gz
        sudo tar -C /usr/local -xzf go1.13.5.linux-amd64.tar.gz
        export PATH=$PATH:/usr/local/go/bin
        source .profile
        rm -rf go1.13.5.linux-amd64.tar.gz
    fi
fi

echo "go version : `go version`"

#-----------------------------
# ライブラリのインストール
#-----------------------------
mkdir -p api
cd api
if [ ! "$(go list -m -u all | grep 'github.com/gin-gonic/gin')" ] ; then
	go mod init api
	go get -u github.com/gin-gonic/gin
fi

#-----------------------------
# スクリプトの実行
#-----------------------------
# コンパイルして実行
#go build main.go

# コンパイルされたファイルを実行
#.main

# コンパイルなしで実行
go run main.go --port ${PORT}
