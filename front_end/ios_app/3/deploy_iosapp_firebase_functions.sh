#!/bin/sh
set -eu
ROOT_DIR=${PWD}
ZONE="us-central1"
PROJECT_ID="ios-sample-project"
FUNCTION_NAME="helloWorld"

XCODE_PROJECT_DIR="${ROOT_DIR}/sample-ios-app-project"
XCODE_PROJECT_NAME="sample-ios-app-project"

cd ${XCODE_PROJECT_DIR}

# npm のインストール（MacOSの場合）
#brew install npm

# Firebase CLI のインストール
#sudo npm install -g firebase-tools

# Firebase へのログイン
firebase login

# Firebase プロジェクトを初期化
if [ ! -e "${XCODE_PROJECT_DIR}/functions" ] ; then
    firebase init
fi

# 動的なウェブサイトをデプロイ
firebase deploy --only functions

# Clud Function の URL を開く
open https://${ZONE}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}

# CocoaPos のインストール
#sudo gem update --system
#sudo gem install compass -n /usr/local/bin
#sudo gem install cocoapods -n /usr/local/bin

# Xcode プロジェクトに Pod ファイルを追加
#cd ${XCODE_PROJECT_DIR}
#pod init

# Pod ファイルを修正

# 追加した Pod をインストールする
#pod install

# *.xcworkspace を開く
#open ${PROJ_NAME}.xcworkspace

