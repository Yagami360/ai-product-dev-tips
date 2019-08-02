#!bin/bash
DIR="${HOME}/GitHub/MachineLearning_PreProcessing_Exercises/io_processing/2/dir"   # 絶対パスで指定
#DIR="dir"  # 相対パスで指定

echo ${DIR}
ls ${DIR} | wc -l

echo ${DIR}/sub_dir1
ls ${DIR}/sub_dir1 | wc -l

echo ${DIR}/sub_dir2
ls ${DIR}/sub_dir2 | wc -l