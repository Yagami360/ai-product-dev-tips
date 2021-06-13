#!/bin/sh
#conda activate pytorch11_py36
set -eu
DATSET_DIR=${PWD}/data/datasets/ATR
mkdir -p ${DATSET_DIR}
mkdir -p ${DATSET_DIR}/JPEGImages
mkdir -p ${DATSET_DIR}/SegmentationClassAug
mkdir -p ${DATSET_DIR}/SegmentationClassAug_rev
mkdir -p ${DATSET_DIR}/list

#--------------
# ATR
#--------------
#<<COMMENTOUT
FILE_ID1=0BzvH3bSnp3E9bmkyU3VoNEFJSWc
FILE_NAME1="ICCV15_fashion_dataset(ATR).zip"
curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${FILE_ID1}" > /dev/null
CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=${FILE_ID1}" -o ${FILE_NAME1}
mv ${FILE_NAME1} ./data/datasets/

cd ./data/datasets/
tar -zxvf ${FILE_NAME1}
rm -rf ${FILE_NAME1}

cp -r humanparsing/* ${DATSET_DIR}

#--------------
# ATR rev
#--------------
FILE_ID2=1iR8Tn69IbDSM7gq_GG-_s11HCnhPkyG3
FILE_NAME2=SegmentationClassAug_rev.rar
curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${FILE_ID2}" > /dev/null
CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=${FILE_ID2}" -o ${FILE_NAME2}
mv ${FILE_NAME2} ${DATSET_DIR}/SegmentationClassAug_rev

cd ${DATSET_DIR}/SegmentationClassAug_rev
#sudo apt-get install unrar
unrar e ${FILE_NAME2}
#rm -rf ${FILE_NAME2}
