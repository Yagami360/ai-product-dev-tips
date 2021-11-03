#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_NAME="react-hook-app1"
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
# React のプロジェクトを作成し、起動する
#-----------------------------
# React のプロジェクトを作成
if [ ! -e ${ROOT_DIR}/${PROJECT_NAME} ] ; then
  npx -y create-react-app ${PROJECT_NAME}
fi

# プロジェクトをビルドする
if [ ${BUILD} != 0 ] ; then
  cd ${ROOT_DIR}/${PROJECT_NAME}
  npm run build
fi

# 作成した React のプロジェクトのサーバーを起動する
cd ${ROOT_DIR}/${PROJECT_NAME}
npm start
