#!/bin/sh
set -eu
PROJECT_NAME="flutter_app"

# Flutter プロジェクトを作成する
if [ ! -e "./${PROJECT_NAME}" ] ; then
 flutter create -t app --project-name ${PROJECT_NAME} ./${PROJECT_NAME}
fi

# iOS エミュレーターを起動する
open -a simulator
sleep 5

# Flutter アプリを起動する
cd ${PROJECT_NAME}
flutter run
