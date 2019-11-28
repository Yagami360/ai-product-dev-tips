#!/bin/sh
set -eu

OUTPUT_DIR=results
if [ -d "${OUTPUT_DIR}" ] ; then
    rm -r ${OUTPUT_DIR}
fi

python expand_human_parsing.py \
    in_human_parsing in_human_keypoints \
    --out_dir ${OUTPUT_DIR} \
    --debug
