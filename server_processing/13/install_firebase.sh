#!/bin/sh
set -eu

npm init

# firebase npm パッケージをインストールし、package.json ファイルに保存
npm install --save firebase

# CLI のインストール
npm install -g firebase-tools

# 
firebase login
firebase init
firebase deploy
