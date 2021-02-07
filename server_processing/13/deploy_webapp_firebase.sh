#!/bin/sh
set -eu

# npm のインストール（MacOSの場合）
#brew install npm

# package.json を作成
npm init

# package.json を元に、npm のパッケージをインストール
sudo npm install --save firebase

#
