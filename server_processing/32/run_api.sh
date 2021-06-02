#!/bin/sh
set -eu
HOST=localhost
PORT=5000
N_WORKERS=1

# FastAPI をインストール
pip install fastapi

# uvicorn をインストール
pip install uvicorn

# gunicorn をインストール
pip install Gunicorn

# FastAPI サーバーを起動
gunicorn app:app --bind ${HOST}:${PORT} -w ${N_WORKERS} -k uvicorn.workers.UvicornWorker --reload