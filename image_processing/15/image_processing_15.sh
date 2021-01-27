#!/bin/sh
set -eu
cd ${HOME}/GitHub/MachineLearning_Tips/image_processing/15

python detect_face_landmark.py \
    in_image out_image \
    --in_predictor_path shape_predictor_68_face_landmarks.dat \
    --marker_size 10 \
    --debug
