#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_ID="sample-app-73cab"

# npm のインストール（MacOSの場合）
#brew install npm

# Firebase CLI のインストール
#sudo npm install -g firebase-tools

# Firebase へのログイン
firebase login --project ${PROJECT_ID}

# Firebase プロジェクトを初期化
if [ ! -e "${ROOT_DIR}/public" ] ; then
    firebase init --project ${PROJECT_ID}
fi

# Firebase Hosting でウェブサイトをデプロイ
firebase deploy --project ${PROJECT_ID}

# Hosting URL を開く
open https://${PROJECT_ID}.web.app
