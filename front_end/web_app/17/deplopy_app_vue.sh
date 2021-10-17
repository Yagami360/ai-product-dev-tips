#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_NAME="calc-app-vue-project"
HOST="localhost"
PORT=8080
BUILD=0
#BUILD=1

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
npm install -g @vue/cli

#-----------------------------
# Vue.js のプロジェクトを作成し、起動する
#-----------------------------
# Vue.js のプロジェクトを作成
if [ ! -e ${ROOT_DIR}/${PROJECT_NAME} ] ; then
  vue create ${PROJECT_NAME}
fi

# Vue.js アプリをデプロイする
if [ ${BUILD} != 0 ] ; then
  cd ${ROOT_DIR}/${PROJECT_NAME}
  npm run build
fi

# Vue.js アプリのサーバーを起動する
cd ${ROOT_DIR}/${PROJECT_NAME}
npm run serve

#-----------------------------
# デプロイしたアプリの Web サイトにアクセスする
#-----------------------------
open http://${HOST}:${PORT}
