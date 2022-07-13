#!/bin/sh
set -eu
AWS_ACCOUNT_ID=735015535886
AWS_PROFILE=Yagami360
REGION="us-west-2"

CACHE_CLUSTER_PORT=6379
CACHE_REPLICA_GROUP_NAME="elasticache-replica-group"

PRIMARY_ENDPOINT_URL="${CACHE_REPLICA_GROUP_NAME}.a5lv69.ng.0001.usw2.cache.amazonaws.com"
READER_ENDPOINT_URL="${CACHE_REPLICA_GROUP_NAME}-ro.a5lv69.ng.0001.usw2.cache.amazonaws.com"

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
# redis-cil をインストール
#=============================
if [ ${OS} = "Mac" ] ; then
    brew install redis
elif [ ${OS} = "Linux" ] ; then
    sudo apt update
    sudo apt install redis-server
fi

#=============================
# キャッシュクラスターのエンドポイントへリクエスト
#=============================
redis-cli -h ${PRIMARY_ENDPOINT_URL} -p ${CACHE_CLUSTER_PORT}
