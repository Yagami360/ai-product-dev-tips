#!/bin/sh
set -eu
cd ${HOME}/GitHub/MachineLearning_PreProcessing_Exercises/image_processing/14

python dilate_image.py \
    in_image out_image_dilate \
    --width 196 --height 256 \
    --dilate_kernel_size 12 \
    --debug

python erode_image.py \
    in_image out_image_erode \
    --width 196 --height 256 \
    --erode_kernel_size 12 \
    --debug

python dilate_image_human_cloth.py \
    in_image_human in_image_human_parsing out_image_human_dilate \
    --width 196 --height 256 \
    --dilate_kernel_size 12 \
    --debug
