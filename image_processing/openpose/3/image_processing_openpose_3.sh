#!/bin/sh
set -eu

python crop_human_upper.py \
    in_human in_human_keypoints \
    --out_dir results \
    --debug
