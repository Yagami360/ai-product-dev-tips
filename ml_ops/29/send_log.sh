#!/bin/sh
set -eu
TAG_NAME=debug.test

# Fluentd にログ送信
echo '{"log_message":"sample"}' | fluent-cat ${TAG_NAME}
