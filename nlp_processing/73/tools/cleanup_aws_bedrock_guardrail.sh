#!/bin/sh
# setup_aws_bedrock_guardrail.sh で作成したガードレールを削除する
set -eux
GUARDRAIL_ID=${BEDROCK_GUARDRAIL_ID:?BEDROCK_GUARDRAIL_ID を設定する}
REGION=${AWS_REGION:-ap-northeast-1}

aws bedrock delete-guardrail --region "${REGION}" --guardrail-identifier "${GUARDRAIL_ID}"
