#!/bin/sh
set -eu
HOST=localhost
PORT=5000

# FastAPI をインストール
pip install fastapi

# uvicorn をインストール
pip install uvicorn

# FastAPI サーバーを起動する
uvicorn app1:app --reload --host ${HOST} --port ${PORT}