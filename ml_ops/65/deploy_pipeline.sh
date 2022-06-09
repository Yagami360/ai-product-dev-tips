#!/bin/sh
set -eu
KEDRO_PROJECT_NAME="kedro_project"
#USE_TEMPLATE=0
USE_TEMPLATE=1

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
# Kedro をインストールする
#-----------------------------
kedro --version &> /dev/null
if [ $? -ne 0 ] ; then
    pip install kedro
    pip install kedro-viz
fi

kedro --version

#-----------------------------
# Kedro プロジェクトを作成する
#-----------------------------
if [ ! -e ${KEDRO_PROJECT_NAME} ] ; then
    if [ ${USE_TEMPLATE} = 0 ] ; then
        kedro new --config config.yml
    else
        kedro new --config config.yml --starter=pandas-iris
    fi
fi

#-----------------------------
# プロジェクトの依存関係をインストール
#-----------------------------
cd ${KEDRO_PROJECT_NAME}
kedro install

#-----------------------------
# Redro を実行する
#-----------------------------
kedro run

#-----------------------------
# kedro-viz で可視化する
#-----------------------------
kedro viz --host 0.0.0.0