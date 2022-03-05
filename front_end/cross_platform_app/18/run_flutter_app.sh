#!/bin/sh
set -eu
PROJECT_NAME="flutter_app"
#PLATFORM="web"
PLATFORM="ios"
#PLATFORM="andriod"
#PLATFORM="all"

# Flutter プロジェクトを作成する
if [ ! -e "./${PROJECT_NAME}" ] ; then
 flutter create -t app --project-name ${PROJECT_NAME} ./${PROJECT_NAME}
fi

if [ ${PLATFORM} = "ios" ] ; then
  # iOS エミュレーターを起動する
  open -a simulator
  sleep 5
elif [ ${PLATFORM} = "all" ] ; then
  # iOS エミュレーターを起動する
  open -a simulator
  sleep 5
fi

# Flutter アプリを起動する
cd ${PROJECT_NAME}

if [ ${PLATFORM} = "web" ] ; then
  flutter run -d chrome
elif [ ${PLATFORM} = "ios" ] ; then
  flutter run -d macOS
elif [ ${PLATFORM} = "all" ] ; then
  flutter run -d all
fi