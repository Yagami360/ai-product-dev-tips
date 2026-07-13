#!/bin/sh
set -eux

# 検知層(Chronos-Bolt) + 説明層(OpenAI 互換 LLM) の 2 段構成を CPU で動かす。
# 説明層は既定でローカル Ollama(http://localhost:11434/v1) を叩く。
#   事前に:  ollama serve  &&  ollama pull qwen3:4b
# LLM を使わず検知だけ試すなら --no-llm を付ける。

cd "$(dirname "$0")"   # どこから呼んでもこのスクリプトのあるディレクトリで実行する

MODEL_ID=${MODEL_ID:-"amazon/chronos-bolt-base"}
LLM_MODEL=${LLM_MODEL:-"qwen3:4b"}
BASE_URL=${BASE_URL:-"http://localhost:11434/v1"}

python detect_and_report.py \
    --device cpu \
    --model-id "${MODEL_ID}" \
    --context-length 96 \
    --threshold 1.0 \
    --plot images/anomaly.png \
    --base-url "${BASE_URL}" \
    --llm-model "${LLM_MODEL}"
