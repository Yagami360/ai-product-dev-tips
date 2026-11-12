#!/bin/sh
# 日本語評価用の Bedrock ガードレール（Standard tier、有害性 5 カテゴリ + PROMPT_ATTACK、いずれも HIGH）を作成し、ID を表示する
# Standard tier は cross-Region inference が必須。東京リージョンから使えるプロファイルは apac.guardrail.v1:0
set -eu  # stdout にガードレール ID だけを出すため -x は付けない
REGION=${AWS_REGION:-ap-northeast-1}
PROFILE_ID=${BEDROCK_GUARDRAIL_PROFILE:-apac.guardrail.v1:0}
NAME=${BEDROCK_GUARDRAIL_NAME:-guard-ja}

aws bedrock create-guardrail --region "${REGION}" \
    --name "${NAME}" \
    --blocked-input-messaging "入力がガードレールによりブロックされました。" \
    --blocked-outputs-messaging "出力がガードレールによりブロックされました。" \
    --cross-region-config "guardrailProfileIdentifier=${PROFILE_ID}" \
    --content-policy-config '{
      "filtersConfig": [
        {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
        {"type": "INSULTS", "inputStrength": "HIGH", "outputStrength": "HIGH"},
        {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
        {"type": "VIOLENCE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
        {"type": "MISCONDUCT", "inputStrength": "HIGH", "outputStrength": "HIGH"},
        {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "NONE"}
      ],
      "tierConfig": {"tierName": "STANDARD"}
    }' \
    --query guardrailId --output text
