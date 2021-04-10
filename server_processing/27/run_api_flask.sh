#!/bin/sh
set -eu
APP_SERVER_HOST=localhost
APP_SERVER_PORT=5000

# Flask のインストール
#sh install.uwsgi.sh

# Flask-API 実行
cd api/
python app.py
