#!/bin/sh
set -eu

OUT_DIR=results

if [ -d "${OUT_DIR}"] ; then
    rm -r ${OUT_DIR}
fi

python dilate_image_human_cloth.py \
    in_human in_human_parsing \
    --out_dir ${OUT_DIR} \
    --width 825 --height 1100 \
    --dilate_kernel_size 32 \
    --debug
