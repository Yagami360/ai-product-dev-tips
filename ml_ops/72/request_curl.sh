#!/bin/sh
set -eu
PORT=5001

curl http://localhost:${PORT}/health
