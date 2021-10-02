#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_ID="graph-cut-web-app"
ZONE="us-central1"
FUNCTION_NAME="call_api"

# npm のインストール（MacOSの場合）
#brew install npm

# Firebase CLI のインストール
#sudo npm install -g firebase-tools

# Firebase へのログイン
firebase login --project ${PROJECT_ID}

# Firebase プロジェクトを初期化
if [ ! -e "${ROOT_DIR}/public" -o ! -e "${ROOT_DIR}/functions" ] ; then
    firebase init --project ${PROJECT_ID}
fi

# firebase cloud function で追加使用する各種モジュールをインストールする
cd ${ROOT_DIR}/functions
if [ ! "npm ls --depth=0 | grep 'request@'" ] ; then
    npm install --save request
fi
if [ ! "npm ls --depth=0 | grep 'request-promise@'" ] ; then
    npm install --save request-promise
fi
cd ${ROOT_DIR}

# CORS 設定ファイルを Web アプリにデプロイする
#gsutil cors set cors.json gs://${PROJECT_ID}.appspot.com
#gsutil cors get gs://${PROJECT_ID}.appspot.com 

# Firebase Hosting でウェブサイトをデプロイ
firebase deploy --project ${PROJECT_ID}

# Hosting URL を開く
#open https://${PROJECT_ID}.web.app

# Clould Function の URL を開く
#open https://${ZONE}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME}
#gcloud functions call ${FUNCTION_NAME}

# Clould Function のログデータを確認する
#open https://console.firebase.google.com/project/${PROJECT_ID}/functions/logs?hl=ja&functionFilter=${FUNCTION_NAME}(${ZONE})&search=&severity=DEBUG
#firebase functions:log --only ${FUNCTION_NAME}

# WebAPI のログデータを確認する
#kubectl logs `kubectl get pods | grep "graph-cut-api-pod" | awk '{print $1}'` graph-cut-api-container
