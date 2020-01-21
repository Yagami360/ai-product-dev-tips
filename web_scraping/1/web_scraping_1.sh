#!/bin/sh
set -eu

URL="https://zalando.com/"
#URL="https://www.zalando.co.uk/clothing/"

OUT_DIR=results

if [ -d "${OUT_DIR}" ] ; then
    rm -r ${OUT_DIR}
fi

python scraping_images.py ${URL} \
    --out_dir ${OUT_DIR} \
    --debug
