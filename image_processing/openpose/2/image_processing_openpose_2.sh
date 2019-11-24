#!/bin/sh
set -eu
cd ${HOME}/GitHub/MachineLearning_PreProcessing_Exercises/image_processing/openpose/2

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
