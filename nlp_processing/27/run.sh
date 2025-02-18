#!/bin/bash
set -eu
export OPENAI_API_KEY=${OPENAI_API_KEY:-"dummy"}

if ! pip3 list | grep -q deepeval; then
    pip3 install deepeval
fi

python3 run.py --threshold 0.3
