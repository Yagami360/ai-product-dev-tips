#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004
INGRESS_NAME=fast-api-rate-limit-ingress
HOST=`kubectl get ingress | grep ${INGRESS_NAME} | awk '{print $4}'`

N_REQUESTS=15
INTERVAL_SEC=1

#-----------------------------------------------
# GCP 環境のデフォルト値の設定
#-----------------------------------------------
gcloud config set project ${PROJECT_ID}
gcloud config list

#-----------------------------------------------
# API を実行する
#-----------------------------------------------
# health check
echo "[GET method] ヘルスチェック\n"
for i in `seq 1 ${N_REQUESTS}`
do
    echo "\nrequest ${i} : "
    curl http://${HOST}/health
    sleep ${INTERVAL_SEC}
done
