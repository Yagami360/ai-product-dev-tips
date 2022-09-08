#!/bin/sh
set -eu
GO_BUILD=0
#GO_BUILD=1

#export GOPATH=$HOME/go
#export PATH=$PATH:$GOPATH/bin
#export PATH=$PATH:/usr/local/go/bin
#source ~/.bashrc

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
#go env

#-----------------------------
# ライブラリのインストール
#-----------------------------
mkdir -p src
cd src
go mod init src
if [ ! "$(go list -m -u all | grep 'github.com/golang/mock')" ] ; then
	go get github.com/golang/mock/gomock
fi

go install github.com/golang/mock/mockgen@v1.6.0
echo "mockgen version : `mockgen -version`"

#-----------------------------
# モックの作成
#-----------------------------
mockgen -source main.go -destination main_mock.go

#-----------------------------
# 単体テスト実行
#-----------------------------
go test -v --cover main_test.go