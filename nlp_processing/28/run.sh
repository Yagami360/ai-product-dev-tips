#!/bin/bash
set -eu
export OPENAI_API_KEY=${OPENAI_API_KEY:-"dummy"}
export DEEPEVAL_API_KEY=${DEEPEVAL_API_KEY:-"dummy"}
export DATASET_NAME=${DATASET_NAME:-"dummy"}

if ! pip3 list | grep -q deepeval; then
    pip3 install deepeval
fi

# deepeval login

python3 run.py --dataset_name ${DATASET_NAME}
