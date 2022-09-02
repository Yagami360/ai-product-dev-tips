#!/bin/sh
set -eu
GO_BUILD=0
#GO_BUILD=1

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
#if [ ! "$(go list -m -u all | grep 'github.com/gin-gonic/gin')" ] ; then
#	go mod init api
#	go get -u github.com/gin-gonic/gin
#fi

#-----------------------------
# スクリプトの実行
#-----------------------------
if [ ${GO_BUILD} = 0 ] ; then
  # コンパイルなしで実行
  go run main_1.go
  go run main_2.go
  go run main_3.go
else
  # コンパイルして実行
  go build main_1.go
  go build main_2.go
  go build main_3.go

  # コンパイルされたファイルを実行
  ./main_1
  ./main_2
  ./main_3
fi
