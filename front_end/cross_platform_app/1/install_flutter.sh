#!/bin/sh
set -eu
ROOT_DIR=${PWD}
INSTALL_PATH=${HOME}
SDK_FILE_NAME="flutter_macos_2.10.0-stable"

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
# Flutter SDK のインストール
#-----------------------------
mkdir -p ${INSTALL_PATH}
cd ${INSTALL_PATH}

if [ ${OS} = "Mac" ] ; then
  if [ ! `brew list | grep wget` ] ; then
    brew install wget
  fi
  # Flutter SDK をダウンロード
  wget https://storage.googleapis.com/flutter_infra_release/releases/stable/macos/${SDK_FILE_NAME}.zip
  unzip ${SDK_FILE_NAME}.zip
  rm -rf ${SDK_FILE_NAME}.zip
  cd ${ROOT_DIR}

  # パスを設定
  echo "" >> ~/.bash_profile
  echo "# flutter sdk のパス設定" >> ~/.bash_profile
  echo "export PATH=""$""PATH":${INSTALL_PATH}/flutter/bin"" >> ~/.bash_profile
  cat ~/.bash_profile
  source ~/.bashrc

  # バージョン確認（要ターミナル再起動）
  which flutter
  flutter doctor
fi
