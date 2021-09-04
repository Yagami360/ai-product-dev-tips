#!/bin/sh
set -eu
VIDEO_HEIGHT=480
IN_VIDEO_FILE_PATH="../in_video/mov_hts-samp005.mp4"
OUT_VIDEO_FILE_PATH="../in_video/mov_hts-samp005_${VIDEO_HEIGHT}p.mp4"

ffmpeg -i ${IN_VIDEO_FILE_PATH} -vf scale=${VIDEO_HEIGHT}:-1 ${OUT_VIDEO_FILE_PATH}
