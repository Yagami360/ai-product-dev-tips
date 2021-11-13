#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_NAME="react-material-ui-app"
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
  npx -y create-react-app ${PROJECT_NAME} --template typescript 
fi
cd ${ROOT_DIR}/${PROJECT_NAME}

# 各種 npm パッケージをインストール
if [ "npm ls --depth=0 | grep -E ' react-router-dom@'*" == "" ] ; then
  npm install --save react-router-dom                       # ルーティング（リダイレクト）用パッケージ
fi
if [ "npm ls --depth=0 | grep -E ' @types/react-router-dom@'*" == "" ] ; then
  npm install --save-dev @types/react-router-dom            # ルーティング（リダイレクト）用パッケージ
fi
if [ "npm ls --depth=0 | grep -E ' @material-ui/core@'*" == "" ] ; then
  npm install --save @material-ui/core    # Material-UI
fi
if [ "npm ls --depth=0 | grep -E ' @material-ui/icons@'*" == "" ] ; then
  npm install --save @material-ui/icons   # Material-UI
fi
npm ls --depth=0

# プロジェクトをビルドする
if [ ${BUILD} != 0 ] ; then
  npm run build
fi

# 作成した React のプロジェクトのサーバーを起動する
npm start
