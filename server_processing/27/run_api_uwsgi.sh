#!/bin/sh
set -eu
UWSGI_SERVER_HOST=localhost
#UWSGI_SERVER_HOST=0.0.0.0
UWSGI_SERVER_PORT=5001
USE_INI_FILE=0

# uWSGI のインストール
pip install uWSGI

# uWSGI で Flask-API 実行
cd api/
if [ ${USE_INI_FILE} = 0 ] ; then
    uwsgi --http=${UWSGI_SERVER_HOST}:${UWSGI_SERVER_PORT} --wsgi-file=app.py --callable=app
else
    uwsgi --ini uwsgi.ini
fi
