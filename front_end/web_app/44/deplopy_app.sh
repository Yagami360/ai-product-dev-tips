#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_NAME="nextjs-app"
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
# React のプロジェクトを作成する
#-----------------------------
# React のプロジェクトを作成
mkdir -p ${PROJECT_NAME}

# `package.json` を作成する
cd ${ROOT_DIR}/${PROJECT_NAME}
rm -rf "package.json"
touch "package.json"
echo '{
  "scripts": {
    "dev": "next",
    "build": "next build",
    "start": "next start",
    "export": "next export"
  }
}' > "package.json"

# next.js, react, bootstrap をインストールする
cd ${ROOT_DIR}/${PROJECT_NAME}
npm install --save next
npm install --save react
npm install react-bootstrap bootstrap
npm ls --depth=0

rm -rf ".gitignore"
touch ".gitignore"
echo 'node_modules' >> ".gitignore"
echo '.next' >> ".gitignore"

# テンプレートファイルを作成する
mkdir -p ${ROOT_DIR}/${PROJECT_NAME}/pages
touch ${ROOT_DIR}/${PROJECT_NAME}/pages/"index.js"

#-----------------------------
# React アプリを起動する
#-----------------------------
# プロジェクトをビルドする
if [ ${BUILD} != 0 ] ; then
  # Next.js の設定ファイル `next.config.js` を作成する
  cd ${ROOT_DIR}/${PROJECT_NAME}
  touch "next.config.js"
  echo 'module.exports = {
    exportPathMap: function () {
      return {
        "/": { page: "/" }
      }
    }
  }' > "next.config.js"

  # プロジェクトをビルドする
  npm run build

  # プロジェクトをエクスポートする
  npm run export
fi

# 作成した Next.js のプロジェクトのサーバーを起動する
cd ${ROOT_DIR}/${PROJECT_NAME}
npm run dev
