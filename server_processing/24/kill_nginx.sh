#!/bin/sh
set -eu

ps aux | grep nginx
ps aux | grep [n]ginx | awk '{ print "sudo kill -9", $2 }'
sudo pkill nginx
