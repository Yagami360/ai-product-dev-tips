#!/bin/sh
set -eu

#=============================
# OS判定
#=============================
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

#=============================
# Python CLI 実行
#=============================
