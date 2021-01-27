#!/bin/sh
set -eu
docker-compose -f pipelines/docker-compose.yml stop
docker-compose -f pipelines/docker-compose.yml up -d
docker exec -it pipeline_container bash
