#!/bin/sh
set -eu
SERVER_USERNAME=ubuntu
SERVER_ADDRESS=100.20.254.22
SERVER_PORT=6006
LOCAL_PORT=6006

ssh -N -L localhost:${LOCAL_PORT}:localhost:${SERVER_PORT} ${SERVER_USERNAME}@${SERVER_ADDRESS}
