#!/bin/sh
# setup_gcp_model_armor.sh で作成した評価用テンプレートを削除する
# Model Armor API はプロジェクト内の他の用途で使っている可能性があるので無効化しない（不要なら gcloud services disable modelarmor.googleapis.com）
set -eux
PROJECT=${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT を設定する}
LOCATION=${MODEL_ARMOR_LOCATION:-asia-northeast1}
TEMPLATE=${MODEL_ARMOR_TEMPLATE:-guard-ja}

curl -fsS -X DELETE \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "x-goog-user-project: ${PROJECT}" \
    "https://modelarmor.${LOCATION}.rep.googleapis.com/v1/projects/${PROJECT}/locations/${LOCATION}/templates/${TEMPLATE}"
