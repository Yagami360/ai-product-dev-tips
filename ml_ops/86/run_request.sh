#!/bin/sh
set -eu

echo "[GET method] ヘルスチェック\n"
curl http://0.0.0.0:4000/api/health
echo "\n"
