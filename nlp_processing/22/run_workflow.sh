#!/bin/bash
set -eu
set encoding=utf-8

export API_URL=${API_URL:-"https://api.dify.ai/v1"}
export API_KEY=${API_KEY:-"dummy"}
# export USER_ID=${USER_ID:-"user-1111111111111"}

# run dify workflow
curl -X POST "${API_URL}/workflows/run" \
    --header "Authorization: Bearer ${API_KEY}" \
    --header "Content-Type: application/json" \
    --data-raw '{
        "inputs": {
            "input_text": "Dify について教えて"
        },
        "response_mode": "streaming",
        "user": "user-1111111111111"
    }'
