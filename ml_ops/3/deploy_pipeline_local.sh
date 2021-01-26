#!/bin/sh
set -eu
#export GOOGLE_APPLICATION_CREDENTIALS="pipelines/src/client_credentials.json"

docker-compose -f pipelines/docker-compose.yml stop
docker-compose -f pipelines/docker-compose.yml up -d
docker exec -it pipeline_container bash
