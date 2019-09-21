#!/bin/sh
set -eu

cd ${HOME}/GitHub/MachineLearning_PreProcessing_Exercises/image_processing/11

python resize_and_crop_wo_mask1.py in_image out_image_A-1_512 --width 512 --height 512 --debug
python resize_and_crop_wo_mask1.py in_image out_image_A-1_256 --width 256 --height 256 --debug

python resize_and_crop_wo_mask2.py in_image out_image_A-2_512_black --width 512 --height 512 --back_ground_color black --debug
python resize_and_crop_wo_mask2.py in_image out_image_A-2_512_white --width 512 --height 512 --back_ground_color white --debug
python resize_and_crop_wo_mask2.py in_image out_image_A-2_256_white --width 256 --height 256 --back_ground_color white --debug

python resize_and_crop_wo_mask3.py in_image out_image_A-3_512_white --width 512 --height 512 --back_ground_color white --debug
python resize_and_crop_wo_mask3.py in_image out_image_A-3_256_white --width 256 --height 256 --back_ground_color white --debug
