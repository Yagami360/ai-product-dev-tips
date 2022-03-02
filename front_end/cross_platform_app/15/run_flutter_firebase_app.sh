#!/bin/sh
set -eu
ROOT_DIR=${PWD}
PROJECT_NAME="flutter_app"
FIREBASE_PROJECT_ID="flutter-app"

#PLATFORM="web"
PLATFORM="ios"
#PLATFORM="andriod"

#-----------------------------
# OS判定
#-----------------------------
if [ "$(uname)" = 'Darwin' ]; then
  OS='Mac'
  echo "Your platform is MacOS."  
elif [ "$(expr substr $(uname -s) 1 5)" = 'Linux' ]; then
  OS='Linux'
  echo "Your platform is Linux."  
elif [ "$(expr substr $(uname -s) 1 10)" = 'MINGW32_NT' ]; then                                                                                           
  OS='Cygwin'
  echo "Your platform is Cygwin."  
else
  echo "Your platform ($(uname -a)) is not supported."
  exit 1
fi

#----------------------------- 
# Flutter
#-----------------------------
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
