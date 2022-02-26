#!/bin/sh
set -eu
PROJECT_NAME="flutter_sample_app"
PLATFORM="web"
#PLATFORM="ios"
#PLATFORM="andriod"

# Flutter プロジェクトを作成する
if [ ! -e "./${PROJECT_NAME}" ] ; then
 flutter create -t app --project-name ${PROJECT_NAME} ./${PROJECT_NAME}
fi

if [ ${PLATFORM} = "web" ] ; then
  killall "iOS Simulator"
  sleep 1
elif [ ${PLATFORM} = "ios" ] ; then
  # iOS エミュレーターを起動する
  open -a simulator
  sleep 5
fi

# Flutter アプリを起動する
cd ${PROJECT_NAME}
flutter run
