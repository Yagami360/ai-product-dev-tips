#!/bin/sh
set -eu
HOST=localhost
PORT=5000

# リクエスト処理を送信
echo "FastAPI サーバーにアクセス"
curl http://${HOST}:${PORT}
