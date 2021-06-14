#!/bin/sh
set -eu
#MAKE_CONF_DEFAULT=0
MAKE_CONF_DEFAULT=1

# OS 判定
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

# Fluentd のインストール
if [ ${OS} = "Mac" ] ; then
    sudo gem install fluentd -n /usr/local/bin
elif [ ${OS} = "Linux" ] ; then
    sudo gem install fluentd -n /usr/local/bin
fi

# Fluentd の設定ファイル `fluent.conf` を作成
if [ ! ${MAKE_CONF_DEFAULT} = 0 ] ; then
    mkdir -p fluent
    fluentd --setup ./fluent
fi

# Fluentd サーバーを起動する
fluentd -c fluent/fluent.conf 
