#!/bin/sh
set -eu
APP_SERVER_HOST=localhost
APP_SERVER_PORT=5000

UWSGI_SERVER_HOST=localhost
UWSGI_SERVER_PORT=5001

# Flask-API サーバーに直接アクセス
echo "Flask-API サーバーに直接アクセス"
curl http://${APP_SERVER_HOST}:${APP_SERVER_PORT}

# uWSGI 経由で Flask-API サーバーにアクセス
echo "uWSGI 経由で Flask-API サーバーにアクセス"
curl http://${UWSGI_SERVER_HOST}:${UWSGI_SERVER_PORT}
