#!/bin/sh
#set -eu

ps aux | grep nginx | grep -v grep | awk '{ print "sudo kill -9", $2 }'
ps aux | grep nginx | grep -v grep | awk '{ print "sudo kill -9", $2 }' | sh
#sudo pkill nginx
