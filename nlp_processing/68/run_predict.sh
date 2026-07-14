#!/bin/sh
set -eux

# SensorLLM(Stage1)の単一サンプル推論を実行するスクリプト。
# 公式実装 cruiseresearchgroup/SensorLLM を clone し、その sensorllm パッケージを
# PYTHONPATH に通して predict.py を実行する。
#
# 前提:
#   - NVIDIA GPU（推論は T4/V100 でも --dtype float16 で可、A100 等なら bfloat16）
#   - Python 3.8+（torch==2.4.1 のため。作成環境の 3.7 では不可）
#   - Hugging Face から公式リポジトリ・非公式チェックポイント・Chronos を DL できること

SENSORLLM_DIR="${SENSORLLM_DIR:-./SensorLLM}"

# 1. 公式リポジトリを clone（未取得なら）
if [ ! -d "${SENSORLLM_DIR}" ]; then
  git clone https://github.com/cruiseresearchgroup/SensorLLM "${SENSORLLM_DIR}"
fi

# 2. 依存をインストール（公式の requirements をそのまま利用）
pip install -r "${SENSORLLM_DIR}/requirements.txt"

# 3. sensorllm パッケージを import できるようにして推論を実行
#    既定: 非公式 Stage1 ckpt(MHealth 学習) + amazon/chronos-t5-large を DL して合成波形で推論
PYTHONPATH="${SENSORLLM_DIR}:${PYTHONPATH:-}" python predict.py \
  --model-path "1EE1/SensorLLM-Stage1-Backup" \
  --chronos-path "amazon/chronos-t5-large" \
  --dataset mhealth \
  --dtype bfloat16 \
  --device cuda

# T4 / V100 で動かす場合は --dtype float16 に変更する:
#   ... python predict.py ... --dtype float16 --device cuda
