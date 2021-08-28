#!/bin/sh
set -eu
HOST=0.0.0.0
PORT=5000

IN_IMAGE_DIR=in_image
IN_VIDEO_DIR=in_video
IN_AUDIO_DIR=in_audio

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 1

# curl コマンドを使用してリクエスト処理
curl -X POST "http://${HOST}:${PORT}/upload_file" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@${IN_IMAGE_DIR}/1.jpg;type=image/jpeg"
curl -X POST "http://${HOST}:${PORT}/upload_file" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@${IN_VIDEO_DIR}/1.mp4;type=video/mp4"
curl -X POST "http://${HOST}:${PORT}/upload_file" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@${IN_AUDIO_DIR}/1.mp3;type=audio/mpeg"

# request　モジュールを使用してリクエスト処理
python request.py --host ${HOST} --port ${PORT} --in_image_dir ${IN_IMAGE_DIR} --in_video_dir ${IN_VIDEO_DIR} --in_audio_dir ${IN_AUDIO_DIR}

docker logs fast-api-container

