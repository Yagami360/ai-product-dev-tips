#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJ_NAME="sample-ios-app-project"
XCODE_PROJ_DIR="${ROOT_DIR}/sample-ios-app-project"

# CocoaPos のインストール
sudo gem update --system
#sudo gem install cocoapods
sudo gem install compass -n /usr/local/bin
sudo gem install cocoapods -n /usr/local/bin

# Xcode プロジェクトに Pod ファイルを追加
cd ${XCODE_PROJ_DIR}
pod init

# Pod ファイルを修正

# 追加した Pod をインストールする
pod install

# 
open ${PROJ_NAME}.xcworkspace
