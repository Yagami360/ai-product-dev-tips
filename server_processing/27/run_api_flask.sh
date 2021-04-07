#!/bin/sh
set -eu
APP_SERVER_HOST=localhost
APP_SERVER_PORT=5000

# Flask のインストール
pip install flask
pip install Flask-Cors

# Flask-API 実行
cd api/
python app.py --host ${APP_SERVER_HOST} --port ${APP_SERVER_PORT} --debug
