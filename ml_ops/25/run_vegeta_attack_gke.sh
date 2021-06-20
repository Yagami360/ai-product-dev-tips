#!/bin/sh
set -eu
POD_NAME=`kubectl get pods | grep vegeta-attack-pod | awk '{print $1}'`

DURATION=60s        # 負荷時間
#RATE=60             # 1sec あたりのリクエスト回数
RATE=1000

# vegeta attack を使用して負荷テスト
# get-target, post-target は、config map で定義した設定値になる
kubectl exec -i ${POD_NAME} -- bash -c "vegeta --version && \
	vegeta attack -duration=${DURATION} -rate=${RATE} -targets=/vegeta/configmap/get-health-target | vegeta report -type=text && \
	vegeta attack -duration=${DURATION} -rate=${RATE} -targets=/vegeta/configmap/get-metadata-target | vegeta report -type=text && \
	vegeta attack -duration=${DURATION} -rate=${RATE} -targets=/vegeta/configmap/post-add_users-target | vegeta report -type=text"
