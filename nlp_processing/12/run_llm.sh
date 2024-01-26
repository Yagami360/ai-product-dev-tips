#!/bin/bash
set -eu
export OPENAI_API_KEY=${OPENAI_API_KEY:-"dummy"}

python3 run_llm.py
