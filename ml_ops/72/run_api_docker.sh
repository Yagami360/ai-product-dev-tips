#!/bin/sh
set -eu
PORT=5001

# Web サーバーを起動する
docker-compose -f docker-compose.yml stop
docker-compose -f docker-compose.yml up -d
sleep 1

# health check 
curl http://localhost:${PORT}/health

#open http://localhost:${PORT}
