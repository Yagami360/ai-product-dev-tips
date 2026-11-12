#!/bin/sh
# 評価用の Azure AI Content Safety リソース（F0 無料枠）を作成し、エンドポイントとキーを .env 形式（KEY=value）で表示する
# 使い方: ./tools/setup_azure_content_safety.sh >> .env
set -eu  # stdout に .env 形式の行だけを出すため -x は付けない
NAME=${AZURE_CONTENT_SAFETY_NAME:?AZURE_CONTENT_SAFETY_NAME（グローバルで一意なリソース名）を設定する}
RG=${AZURE_RESOURCE_GROUP:-rg-guardrail-test}
LOCATION=${AZURE_LOCATION:-japaneast}

az group create -n "${RG}" -l "${LOCATION}" -o none
az cognitiveservices account create -n "${NAME}" -g "${RG}" \
    --kind ContentSafety --sku F0 -l "${LOCATION}" --custom-domain "${NAME}" --yes -o none

echo "AZURE_CONTENT_SAFETY_ENDPOINT=https://${NAME}.cognitiveservices.azure.com/"
echo "AZURE_CONTENT_SAFETY_KEY=$(az cognitiveservices account keys list -n "${NAME}" -g "${RG}" --query key1 -o tsv)"
