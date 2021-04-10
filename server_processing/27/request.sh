#!/bin/sh
#set -eu
APP_SERVER_HOST=localhost
APP_SERVER_PORT=5000

UWSGI_SERVER_HOST=localhost
UWSGI_SERVER_PORT=5001

# OS 判定
if [ "$(uname)" = 'Darwin' ]; then
  OS='Mac'
  echo "Your platform is MacOS."  
elif [ "$(expr substr $(uname -s) 1 5)" = 'Linux' ]; then
  OS='Linux'
  echo "Your platform is Linux."  
elif [ "$(expr substr $(uname -s) 1 10)" = 'MINGW32_NT' ]; then                                                                                           
  OS='Cygwin'
  echo "Your platform is Cygwin."  
else
  echo "Your platform ($(uname -a)) is not supported."
  exit 1
fi

# Flask-API サーバーに直接アクセス
echo "Flask-API サーバーに直接アクセス"
curl http://${APP_SERVER_HOST}:${APP_SERVER_PORT}

# uWSGI 経由で Flask-API サーバーにアクセス
echo "uWSGI 経由で Flask-API サーバーにアクセス"
curl http://${UWSGI_SERVER_HOST}:${UWSGI_SERVER_PORT}

if [ ${OS} = 'Mac' ]; then
    open http://${APP_SERVER_HOST}:${APP_SERVER_PORT}
    open http://${UWSGI_SERVER_HOST}:${UWSGI_SERVER_PORT}
fi