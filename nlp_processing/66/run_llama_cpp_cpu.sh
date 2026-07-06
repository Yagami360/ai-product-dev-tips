#!/bin/sh
set -eux

# =============================================================================
# CPU で軽量量子化版 MiniMax-M3（GGUF）を llama.cpp で動かすための
# ビルド＆OpenAI 互換サーバー（llama-server）起動スクリプト。
#   - MiniMax-M3 の GGUF は 2026/7 時点で llama.cpp 本体未マージのため、対応 PR ブランチをビルドする。
#   - CPU 実行のため CUDA を OFF にしてビルドする（-DGGML_CUDA=OFF）。
#   - 428B の MoE のため、最小の 1-bit 量子化（UD-IQ1_M ≈ 128GB）でも約 133GB の RAM が要る。
# =============================================================================

# 使う量子化タグ（軽い順）:
#   UD-IQ1_M  (1bit, ≈128GB, 要RAM≈133GB) / UD-IQ3_XXS (3bit, ≈159GB)
#   UD-IQ4_XS (4bit, ≈208GB) / UD-Q4_K_XL (4bit, ≈265GB)
QUANT="${QUANT:-unsloth/MiniMax-M3-GGUF:UD-IQ1_M}"
PORT="${PORT:-8080}"
CTX="${CTX:-8192}"

# 1) MiniMax-M3 対応ブランチの llama.cpp をビルド（CPU 版）
if [ ! -x "llama.cpp/build/bin/llama-server" ]; then
  if [ ! -d "llama.cpp" ]; then
    git clone https://github.com/ggml-org/llama.cpp
  fi
  cd llama.cpp
  git fetch origin pull/24523/head:minimax-m3
  git checkout minimax-m3
  cmake -B build -DGGML_CUDA=OFF
  cmake --build build --config Release -j --target llama-cli llama-server
  cd ..
fi

# 2) OpenAI 互換サーバーを起動（初回は GGUF を自動ダウンロード）
#    起動後、別ターミナルで `python predict_local.py` を叩く。
./llama.cpp/build/bin/llama-server \
  -hf "${QUANT}" \
  --host 0.0.0.0 --port "${PORT}" \
  --ctx-size "${CTX}" \
  --temp 1.0 --top-p 0.95 --top-k 40
