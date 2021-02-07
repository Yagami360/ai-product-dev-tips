#!/bin/sh
set -eu
ZONE="us-central1"
PROJECT_ID="sample-app-73cab"
FUNCTION_NAME="helloWorld"

# npm のインストール（MacOSの場合）
#brew install npm

# Firebase CLI のインストール
#sudo npm install -g firebase-tools

# Firebase へのログイン
firebase login

# Firebase プロジェクトを初期化
firebase init

# 動的なウェブサイトをデプロイ
firebase deploy --only functions

# Clud Function の URL を開く
open https://${ZONE}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}
