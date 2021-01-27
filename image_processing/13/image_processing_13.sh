#!/bin/sh
set -eu
cd ${HOME}/GitHub/MachineLearning_Tips/image_processing/13

python scale_image_pillow.py in_image out_image_scale_pillow \
--n_scale 5 \
--init_width 1024 --init_height 1024 \
--scale_rate 0.75 \
--back_ground_color black \
--debug

python offset_image_pillow.py in_image out_image_offset_width_pillow \
--n_offset 5 \
--offset_init_width -200 --offset_init_height 0 \
--offset_width 50 --offset_height 0 \
--debug

python offset_image_pillow.py in_image out_image_offset_height_pillow \
--n_offset 5 \
--offset_init_width 0 --offset_init_height -50 \
--offset_width 0 --offset_height 20 \
--debug

python rotate_image_pillow.py in_image out_image_rot_pillow \
--n_rotate 5 \
--debug