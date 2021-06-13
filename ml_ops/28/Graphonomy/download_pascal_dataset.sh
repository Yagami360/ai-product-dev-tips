# CIHP
<<COMMENTOUT
FILE_ID=2fa0a19ee9b5e43b2bee520166111120
FILE_NAME=trainval.tar.gz
curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${FILE_ID}" > /dev/null
CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=${FILE_ID}" -o ${FILE_NAME}

mv ${FILE_NAME} ./data/datasets/
cd ./data/datasets/
tar -zxvf ${FILE_NAME}
rm -rf ${FILE_NAME}

mv -r VOCdevkit pascal/
COMMENTOUT
