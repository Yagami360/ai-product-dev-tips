#!/bin/sh
set -eu
SERVICE_NAME=fast-api-server
PORT=5000
DURATION=60s        # 負荷時間
#RATE=60             # 1sec あたりのリクエスト回数
RATE=500
#RATE=1000

# 公開外部アドレス取得
EXTERNAL_IP=`kubectl describe service ${SERVICE_NAME} | grep "LoadBalancer Ingress" | awk '{print $3}'`

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

# vegeta attack のインストール
if [ ${OS} = "Mac" ] ; then
    brew install vegeta
elif [ ${OS} = "Linux" ] ; then
    wget https://github.com/tsenart/vegeta/releases/download/cli%2Fv12.3.0/vegeta-12.3.0-linux-amd64.tar.gz
    tar xf vegeta-12.3.0-linux-amd64.tar.gz
fi

vegeta --version

# vegeta attack を使用して負荷テスト
echo "[GET method] ヘルスチェック\n"
echo "GET http://${EXTERNAL_IP}:${PORT}/health" | vegeta attack -duration=${DURATION} -rate=${RATE} | vegeta report -type=text

echo "[GET method] metadata 取得\n"
echo "GET http://${EXTERNAL_IP}:${PORT}/metadata" | vegeta attack -duration=${DURATION} -rate=${RATE} | vegeta report -type=text

#echo "[POST method] ユーザー追加\n"
echo "POST http://${EXTERNAL_IP}:${PORT}/add_users Content-Type: application/json {'id':4, 'name':'user4', 'age':'100'}" | vegeta attack -duration=${DURATION} -rate=${RATE} | vegeta report -type=text
