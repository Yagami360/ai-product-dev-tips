#!/bin/sh
set -eu

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
