#!/bin/sh
# 参考 : https://qiita.com/namakemono/items/c963e75e0af3f7eed732
set -eu

FILE_ID=1eNpTES0RmruLZO06-5Mp7U44oN8gsPk4
FILE_NAME=traindata.tar.gz

curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${FILE_ID}" > /dev/null
CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=${FILE_ID}" -o ${FILE_NAME}
