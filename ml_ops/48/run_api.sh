#!/bin/sh
set -eu
HOST=0.0.0.0
PORT=5000
N_POLLINGS=100

IN_VIDEO_DIR=in_video
OUT_VIDEO_DIR=out_video
rm -rf ${OUT_VIDEO_DIR}

# API 起動
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 5

# ヘルスチェック
curl http://${HOST}:${PORT}/health

# リクエスト処理
python request.py --host ${HOST} --port ${PORT} --in_video_dir ${IN_VIDEO_DIR} --out_video_dir ${OUT_VIDEO_DIR} --n_pollings ${N_POLLINGS}

#docker-compose logs --tail 50
#docker logs proxy-video-container
#docker logs batch-video-container
