#!bin/bash
DIR="${HOME}/GitHub/MachineLearning_PreProcessing_Exercises/io_processing/2/dir"   # 絶対パスで指定
#DIR="dir"  # 相対パスで指定

ls ${DIR} | while read name

do
echo $name
done

ls ${DIR} | while read name; do echo $name; ls ${DIR} -1 $name | wc -l; done
