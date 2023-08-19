#!/bin/sh
set -eu
API_URL="http://0.0.0.0:5000"

# get ai-plugin.json
curl -X GET "${API_URL}/.well-known/ai-plugin.json"

# get openapi.yaml
curl -X GET "${API_URL}/openapi.yaml"

# get plugin_logo
curl -X GET "${API_URL}/logo.png" --output "logo.png"

# add todo
curl -X POST -H "Content-Type: application/json" -d '{"todo" : "go shopping"}' ${API_URL}/todos/yagami

# get todo
curl -X GET "${API_URL}/todos/yagami"

# delete todo
curl -X DELETE -H "Content-Type: application/json" -d '{"todo_idx" : 1}' "${API_URL}/todos/yagami"
