#!/bin/sh
set -eu
#SQL_INSTANCE_NAME=mysql-instance-220528
SQL_INSTANCE_NAME="mysql-instance-$(date "+%Y%m%d")"

#-----------------------------------------------
# SQL インスタンスへ接続する
#-----------------------------------------------
gcloud sql connect ${SQL_INSTANCE_NAME} --user=root
