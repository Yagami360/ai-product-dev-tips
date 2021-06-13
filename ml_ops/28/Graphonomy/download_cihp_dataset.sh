#--------------
# CIHP
#--------------
#<<COMMENTOUT
FILE_ID1=1HdqA8yWVxZ8od0hngKzZTziHx_ONzCWj
FILE_NAME1=instance-level_human_parsing.tar.gz
curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${FILE_ID1}" > /dev/null
CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=${FILE_ID1}" -o ${FILE_NAME1}
mv ${FILE_NAME1} ./data/datasets/

cd ./data/datasets/
tar -zxvf ${FILE_NAME1}
rm -rf ${FILE_NAME1}

cp -r instance-level_human_parsing/Training/* CIHP_4w/
mv CIHP_4w/train_id.txt CIHP_4w/lists

cp -r instance-level_human_parsing/Validation/* CIHP_4w/
mv CIHP_4w/val_id.txt CIHP_4w/lists

cp -r instance-level_human_parsing/Testing/* CIHP_4w/
mv CIHP_4w/test_id.txt CIHP_4w/lists
#COMMENTOUT

#--------------
# CIHP rev
#--------------
FILE_ID2=1aaJyQH-hlZEAsA7iH-mYeK1zLfQi8E2j
FILE_NAME2=Category_rev_ids.rar
curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${FILE_ID2}" > /dev/null
CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=${FILE_ID2}" -o ${FILE_NAME2}
mv ${FILE_NAME2} ./data/datasets/CIHP_4w/Category_rev_ids

#cd ./data/datasets/CIHP_4w/Category_rev_ids
#sudo apt-get install unrar
#unrar e ${FILE_NAME2}
#rm -rf ${FILE_NAME2}
