#!/bin/sh
# setup_azure_content_safety.sh で作成したリソースグループを削除し、論理削除された Content Safety リソースを完全に削除（purge）する
# purge しないと、同じリソース名（カスタムドメイン）を 48 時間再利用できない
set -eux
NAME=${AZURE_CONTENT_SAFETY_NAME:?AZURE_CONTENT_SAFETY_NAME を設定する}
RG=${AZURE_RESOURCE_GROUP:-rg-guardrail-test}
LOCATION=${AZURE_LOCATION:-japaneast}

az group delete -n "${RG}" --yes
az cognitiveservices account purge -n "${NAME}" -g "${RG}" -l "${LOCATION}"
