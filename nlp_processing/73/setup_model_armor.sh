#!/bin/sh
# Model Armor API を有効化し、日本語評価用のテンプレート（RAI 4 カテゴリ + PI/jailbreak、いずれも MEDIUM_AND_ABOVE）を作成する
set -eux
PROJECT=${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT を設定する}
LOCATION=${MODEL_ARMOR_LOCATION:-asia-northeast1}
TEMPLATE=${MODEL_ARMOR_TEMPLATE:-guard-ja}

gcloud services enable modelarmor.googleapis.com --project "${PROJECT}"

curl -fsS -X POST \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "x-goog-user-project: ${PROJECT}" \
    -H "Content-Type: application/json" \
    "https://modelarmor.${LOCATION}.rep.googleapis.com/v1/projects/${PROJECT}/locations/${LOCATION}/templates?templateId=${TEMPLATE}" \
    -d '{
      "filterConfig": {
        "raiSettings": {"raiFilters": [
          {"filterType": "HATE_SPEECH", "confidenceLevel": "MEDIUM_AND_ABOVE"},
          {"filterType": "HARASSMENT", "confidenceLevel": "MEDIUM_AND_ABOVE"},
          {"filterType": "SEXUALLY_EXPLICIT", "confidenceLevel": "MEDIUM_AND_ABOVE"},
          {"filterType": "DANGEROUS", "confidenceLevel": "MEDIUM_AND_ABOVE"}
        ]},
        "piAndJailbreakFilterSettings": {"filterEnforcement": "ENABLED", "confidenceLevel": "MEDIUM_AND_ABOVE"}
      }
    }'
