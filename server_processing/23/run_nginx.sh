#!/bin/sh
set -eu
ROOT_DIR=${PWD}
DAYS=3650
FILE_NAME=server
NGINX_CONF_FILE_PATH="${ROOT_DIR}/nginx/nginx.conf"
PORT=8080
KILL_NGINX_PROCESS=0

#------------------
# OS 判定
#------------------
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

#------------------
# nginx の設定
#------------------
mkdir -p ${ROOT_DIR}/open_ssl
cd ${ROOT_DIR}/open_ssl

# open ssl をインストール
if [ ${OS} = "Mac" ] ; then
    brew install openssl
else
    sudo apt install openssl
fi

# open ssl のバージョン確認
which openssl
openssl version

# 秘密鍵（*.key）を作成
openssl genrsa -out ${FILE_NAME}.key 2048

# 【省略可】公開鍵を作成
openssl rsa -in ${FILE_NAME}.key -pubout -out ${FILE_NAME}_public.key

# 証明書署名要求（*.csr）の作成
openssl req -new -key ${FILE_NAME}.key -out ${FILE_NAME}.csr

# SSL証明書（*.crt）への署名
openssl x509 -req -days ${DAYS} -in ${FILE_NAME}.csr -signkey ${FILE_NAME}.key -out ${FILE_NAME}.crt
openssl x509 -text -in ${FILE_NAME}.crt

# Subject Alternative Name (SAN) で複数ホストに対応する
# Chrome で https サイトにアクセスした場合の `NET::ERR_CERT_COMMON_NAME_INVALID` エラー回避
touch ${FILE_NAME}_san.txt
echo "subjectAltName = DNS:*.com, IP:0.0.0.0" > ${FILE_NAME}_san.txt
openssl x509 -req -days ${DAYS} -in ${FILE_NAME}.csr -signkey ${FILE_NAME}.key -out ${FILE_NAME}.crt -extfile ${FILE_NAME}_san.txt
openssl x509 -text -in ${FILE_NAME}.crt

#------------------
# nginx の設定
#------------------
cd ${ROOT_DIR}

# nginx のインストール
if [ ${OS} = 'Mac' ]; then
    brew install nginx
fi

# nginx のバージョン確認
nginx -v

# nginx プロセス確認
#ps aux | grep nginx

# nginx 停止
set +e
sudo nginx -s quit
set -e

# nginx 関連のプロセスを全て kill | sudo nginx -s quit でも停止できないときのための処理
if [ ${KILL_NGINX_PROCESS} = 1 ] ; then
    ps aux | grep [n]ginx | awk '{ print "sudo kill -9", $2 }'
    sudo pkill nginx
    sleep 1
fi

# Nginx の Web サーバーを起動
sudo nginx -c ${NGINX_CONF_FILE_PATH}
#sudo nginx -s reload

# Nginx の Web サーバーにブラウザアクセス
#curl https://localhost:${PORT}
if [ ${OS} = 'Mac' ]; then
    sleep 1
    open https://localhost:${PORT}
fi
