#!/bin/sh
set -eu

python check_human_backpose.py \
    in_human in_human_keypoints \
    --out_dir results_nose \
    --check_nose \
    --debug

python check_human_backpose.py \
    in_human in_human_keypoints \
    --out_dir results_shoulder \
    --check_shoulder

python check_human_backpose.py \
    in_human in_human_keypoints \
    --out_dir results_hip \
    --check_hip

python check_human_backpose.py \
    in_human in_human_keypoints \
    --out_dir results_knee \
    --check_knee
