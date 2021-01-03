#!/bin/sh
set -eu

docker-compose -f api/docker-compose.yml stop
docker-compose -f api/docker-compose.yml up -d
#docker exec -it sample_container bash

sleep 1
python request.py --host 0.0.0.0 --port 5000 --debug
