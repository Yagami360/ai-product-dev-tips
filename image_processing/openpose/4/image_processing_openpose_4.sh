#!/bin/sh
set -eu

python check_cloth_shorts.py \
    in_human in_human_parsing in_human_keypoints \
    --out_dir results \
    --debug
