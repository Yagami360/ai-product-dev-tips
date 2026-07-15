#!/bin/sh
set -eux

# SensorLLM(Stage1)の単一サンプル推論を実行するスクリプト。
# 公式実装 cruiseresearchgroup/SensorLLM を clone し、その sensorllm パッケージを
# PYTHONPATH に通して predict.py を実行する。
#
# 前提:
#   - Python 3.8+（torch==2.4.1 のため）
#   - GPU: 推論は CPU/T4/V100 でも可（--device cpu --dtype float32、または fp16）。
#          A100 等 Ampere なら --dtype bfloat16。CPU 実機でも動作確認済み。
#   - Hugging Face から公式リポジトリ・非公式チェックポイント・Chronos を DL できること
#     （下記「HF Xet ダウンロード対策」参照）

SENSORLLM_DIR="${SENSORLLM_DIR:-./SensorLLM}"

# 1. 公式リポジトリを clone（未取得なら）
if [ ! -d "${SENSORLLM_DIR}" ]; then
  git clone https://github.com/cruiseresearchgroup/SensorLLM "${SENSORLLM_DIR}"
fi

# 2. 依存をインストール（推論だけなら flash_attn は不要なので除外して可）
pip install -r "${SENSORLLM_DIR}/requirements.txt"
# HF Xet ダウンロード対策: hf_xet を入れておく（未導入だと Xet 取得がハングしやすい）
pip install hf_xet

# 3. 非公式 ckpt(1EE1)は chronos-t5-base(d_model=768)で学習されているため、
#    ts_backbone.yaml を base(768) に合わせる（既定は large=1024。不一致だと ts_proj で size mismatch）
YAML="${SENSORLLM_DIR}/sensorllm/model/ts_backbone.yaml"
sed -i 's/name: "chronos-t5-large"/name: "chronos-t5-base"/; s/encoder_output_dim: 1024/encoder_output_dim: 768/' "${YAML}"

# 4. sensorllm パッケージを import できるようにして推論を実行
#    既定: 非公式 Stage1 ckpt(MHealth 学習) + amazon/chronos-t5-base を DL して合成波形で推論
PYTHONPATH="${SENSORLLM_DIR}:${PYTHONPATH:-}" python predict.py \
  --model-path "1EE1/SensorLLM-Stage1-Backup" \
  --chronos-path "amazon/chronos-t5-base" \
  --dataset mhealth \
  --dtype float32 \
  --device cpu

# GPU で動かす場合（A100 等）: --dtype bfloat16 --device cuda
# T4 / V100 の場合:            --dtype float16  --device cuda
#
# ------------------------------------------------------------------
# 【HF Xet ダウンロード対策】
# 1EE1 等の Xet ストレージ配信リポジトリは、HF の CDN エッジ us.gcp.cdn.hf.co が
# 署名鍵を "403 SignatureError: invalid key pair id" で拒否することがあり（HF側の
# 一過性インフラ問題）、hf_hub の Xet 取得がハング/失敗する場合がある。
# その場合は、正常な cas-bridge.xethub.hf.co に当たるまで resolve をリトライする方法で回避できる:
#   - 対象ファイルを https://huggingface.co/<repo>/resolve/main/<file> で resolve し、
#     リダイレクト先ホストが cas-bridge.xethub.hf.co のときだけ本体を取得（us.gcp.cdn は再試行）。
#   - resolve は高速連打すると us.gcp.cdn に固定されるため、0.5 秒程度の間隔を空ける。
# もしくは時間を置いて再試行する（HF 側で復旧することが多い）。
