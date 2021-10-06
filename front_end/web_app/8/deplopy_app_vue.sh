#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_NAME="vue-sample-project"
HOST="localhost"
PORT=8080

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
# npm をインストール
#-----------------------------
if [ ${OS} = "Mac" ] ; then
    if [ ! "brew list | grep node" ] ; then
        brew install node
    fi
fi

npm -v

#-----------------------------
# Vue.js の CLI をインストール
#-----------------------------
npm install --global vue-cli

#-----------------------------
# Vue.js のプロジェクトを作成し、起動する
#-----------------------------
# Vue.js のプロジェクトを作成
vue init webpack ${PROJECT_NAME}

# 依存関係をインストールして、起動
cd ${PROJECT_NAME}
npm run dev

#-----------------------------
# デプロイしたアプリの Web サイトにアクセスする
#-----------------------------
open http://${HOST}:${PORT}
