#!/bin/sh
set -eu
PROJECT_NAME="phoenix_websocket_api"

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
# Elixir をインストールする
#-----------------------------
elixir --version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        brew install elixir
    elif [ ${OS} = "Linux" ] ; then
        # Erlang をインストール
        wget https://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb && sudo dpkg -i erlang-solutions_1.0_all.deb
        sudo apt-get update
        sudo apt-get install esl-erlang

        # elixir をインストール
        sudo apt-get install elixir
    fi
fi
echo "elixir version : `elixir --version`"

#-----------------------------
# node.js をインストールする
#-----------------------------
npm --version &> /dev/null
if [ $? -ne 0 ] ; then
    if [ ${OS} = "Mac" ] ; then
        brew install node
    elif [ ${OS} = "Linux" ] ; then
        sudo apt update
        sudo apt install nodejs
        sudo apt install npm
    fi
fi
echo "npm version : `npm --version`"

#-----------------------------
# Phoenix
#-----------------------------
# Phoenix をインストールする
mix phx.new -v &> /dev/null
if [ $? -ne 0 ] ; then
    mix local.hex --force
    mix archive.install hex phx_new --force
fi
mix phx.new -v

# Elixir プロジェクトを作成する
if [ ! ${PROJECT_NAME} ] ; then
    mix phx.new ${PROJECT_NAME}
fi

# Phoenix サーバーを起動する
# cd ${PROJECT_NAME}
# mix phx.server
