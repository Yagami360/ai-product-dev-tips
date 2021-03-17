#!/bin/sh
set -eu
FILE_NAME=server
DAYS=3650
ROOT_DIR=${PWD}

mkdir -p ${ROOT_DIR}/api/open_ssl
cd ${ROOT_DIR}/api/open_ssl

# OS 判定
if [ "$(uname)" == 'Darwin' ]; then
  OS='Mac'
elif [ "$(expr substr $(uname -s) 1 5)" == 'Linux' ]; then
  OS='Linux'
elif [ "$(expr substr $(uname -s) 1 10)" == 'MINGW32_NT' ]; then                                                                                           
  OS='Cygwin'
else
  echo "Your platform ($(uname -a)) is not supported."
  exit 1
fi

# open ssl をインストール
if [ ${OS} = "Mac" ] ; then
    brew install openssl
else
    sudo apt install openssl
fi

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

cd ${ROOT_DIR}
