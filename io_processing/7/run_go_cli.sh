#!/bin/sh
set -eu
GO_BUILD=0
#GO_BUILD=1

CLI_NAME="my-go-cli"
SUB_COMMAND_NAME_1="command1"
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
if [ ! "$(go list -m -u all | grep 'github.com/spf13/cobra')" ] ; then
	go mod init ${CLI_NAME}
	go get -u github.com/spf13/cobra@latest
fi

# cobra-cli をインストール
go install github.com/spf13/cobra-cli@latest

#-----------------------------
# cobra プロジェクト
#-----------------------------
# cobra のプロジェクトを作成する
#cobra init
~/go/bin/cobra-cli init

# サブコマンドを追加
#cobra add ${SUB_COMMAND_NAME_1}
~/go/bin/cobra-cli add ${SUB_COMMAND_NAME_1}

#-----------------------------
# ルートコマンドの実行
#-----------------------------
if [ ${GO_BUILD} = 0 ] ; then
	# コンパイルなしで実行
	go run main.go
else
	# コンパイル
	go build main.go -o ${CLI_NAME}

	# コンパイルされたファイルを実行
	./${CLI_NAME}
fi

#-----------------------------
# サブコマンドの実行
#-----------------------------
if [ ${GO_BUILD} = 0 ] ; then
	# コンパイルなしで実行
	go run main.go ${SUB_COMMAND_NAME_1}
else
	# コンパイル
	go build main.go -o ${CLI_NAME}

	# コンパイルされたファイルを実行
	./${CLI_NAME} ${SUB_COMMAND_NAME_1}
fi

