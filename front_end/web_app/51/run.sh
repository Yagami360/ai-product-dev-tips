#!/bin/sh
set -eu
PROJECT_DIR=$(cd $(dirname $0)/..; pwd)


cd $PROJECT_DIR

python3 -m http.server
