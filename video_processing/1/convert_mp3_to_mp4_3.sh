#!/bin/sh
set -eu

IN_IMAGE_FILE="in_image/1.jpg"
IN_AUDIO_FILE="in_audio/1.mp3"
OUT_VIDEO_FILE="out_video/1.mp4"
FPS=10

mkdir -p `dirname ${OUT_VIDEO_FILE}`

# python-ffmpeg をインストール
pip install ffmpeg-python

# python-ffmpeg を使用した変換処理
python convert_mp3_to_mp4_3.py --in_image_file ${IN_IMAGE_FILE} --in_audio_file ${IN_AUDIO_FILE} --out_video_file ${OUT_VIDEO_FILE} --fps ${FPS}