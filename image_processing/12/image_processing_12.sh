#!/bin/sh
set -eu
cd ${HOME}/GitHub/MachineLearning_Tips/image_processing/12

python alpha_blend_image_and_parse.py in_image in_image_parse out_image_alpha_0_25 --alpha 0.25 --debug
python alpha_blend_image_and_parse.py in_image in_image_parse out_image_alpha_0_5 --alpha 0.5 --debug
python alpha_blend_image_and_parse.py in_image in_image_parse out_image_alpha_0_75 --alpha 0.75 --debug
