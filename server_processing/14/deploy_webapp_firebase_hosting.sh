#!/bin/sh
set -eu
PROJECT_ID="sample-app-73cab"

# npm のインストール（MacOSの場合）
#brew install npm

# Firebase CLI のインストール
#sudo npm install -g firebase-tools

# Firebase へのログイン
firebase login

# Firebase プロジェクトを初期化
firebase init

# Firebase Hosting でウェブサイトをデプロイ
firebase deploy

# Hosting URL を開く
open https://${PROJECT_ID}.web.app
