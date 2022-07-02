#!/bin/sh
set -eu
PORT=3000

curl http://localhost:${PORT}/health
