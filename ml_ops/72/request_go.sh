#!/bin/sh
set -eu
PORT=5001

go run request.go --host 0.0.0.0 --port ${PORT}
