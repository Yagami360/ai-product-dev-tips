#!/bin/sh
set -eu
#APPROX_TYPE=simple
APPROX_TYPE=tc89_l1
#APPROX_TYPE=tc89_kcos
CONTOUR_TYPE=outer
#CONTOUR_TYPE=inner
#CONTOUR_TYPE=all_split
EPSILON=0.001

mkdir -p results
OUT_DIR=results/approx-${APPROX_TYPE}_contour-${CONTOUR_TYPE}_epsilon${EPSILON}

if [ -d "${OUT_DIR}" ] ; then
    rm -r ${OUT_DIR}
fi

python approx_contours_PolyDP.py \
    --in_dir in_image \
    --out_dir ${OUT_DIR} \
    --approx_type ${APPROX_TYPE} \
    --contour_type ${CONTOUR_TYPE} \
    --epsilon ${EPSILON} \
    --debug

