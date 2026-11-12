# ローカルガードレールモデルの日本語実測比較（CPU / GPU）
# パッケージ管理は uv。Ollama 系モデルは事前に `make pull-ollama-models`（GPU 用は `make pull-ollama-models-gpu`）で取得する。

TASK ?= pi
MODEL ?= horizon-pi-guard
N_HARM ?= 200
# 先頭 N 件だけで動作確認する場合に指定（例: make run MODEL=qwen3guard-gen-8b LIMIT=2）
LIMIT ?=
DEVICE ?= cpu
# transformers 系の精度（auto = cuda なら bfloat16、cpu なら float32）。CPU で 8B モデルを動かす場合は bfloat16（float32 だと約 32GB 必要）
DTYPE ?= auto
# torch のビルド（cpu | gpu）。GPU で動かす場合は make install TORCH=gpu で入れ直す
TORCH ?= $(if $(filter cuda,$(DEVICE)),gpu,cpu)

PI_MODELS := horizon-pi-guard protectai-deberta-pi qwen3guard-gen-0.6b llama-guard3-1b shieldgemma-2b granite3-guardian-2b
HARM_MODELS := qwen3guard-gen-0.6b llama-guard3-1b shieldgemma-2b granite3-guardian-2b
OLLAMA_MODELS := llama-guard3:1b shieldgemma:2b granite3-guardian:2b

# GPU 推奨の大型モデル（両タスクで評価する）
GPU_MODELS := qwen3guard-gen-4b qwen3guard-gen-8b nemotron-safety-guard-8b gpt-oss-safeguard-20b
OLLAMA_MODELS_GPU := gpt-oss-safeguard:20b

.PHONY: help install lint format format-check pull-ollama-models pull-ollama-models-gpu run run-all run-all-gpu clean

help:         ## タスク一覧を表示
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-24s\033[0m %s\n",$$1,$$2}'

install:      ## 依存(+dev ツール)を uv で仮想環境に同期（GPU 版 torch は TORCH=gpu）
	uv sync --extra dev --extra $(TORCH)

lint: install  ## flake8 / mypy で静的チェック
	uv run flake8 .
	uv run mypy .

format: install  ## black / isort で自動整形
	uv run black .
	uv run isort .

format-check: install  ## 整形済みか確認（CI 用・変更しない）
	uv run black --check .
	uv run isort --check-only .

pull-ollama-models:  ## Ollama 経由で使うガードモデルを取得
	for m in $(OLLAMA_MODELS); do ollama pull $$m; done

pull-ollama-models-gpu:  ## GPU 推奨の Ollama モデル（gpt-oss-safeguard:20b）を取得
	for m in $(OLLAMA_MODELS_GPU); do ollama pull $$m; done

run:          ## 1 モデルを評価（例: make run TASK=harm MODEL=llama-guard3-1b / MODEL=qwen3guard-gen-8b DEVICE=cuda）
	uv run --extra $(TORCH) python evaluate_guard.py --task $(TASK) --model $(MODEL) --n-harm $(N_HARM) --device $(DEVICE) --dtype $(DTYPE) $(if $(LIMIT),--limit $(LIMIT))

run-all:      ## 全モデル × 全タスクを評価して results/ に保存
	for m in $(PI_MODELS); do uv run --extra $(TORCH) python evaluate_guard.py --task pi --model $$m || exit 1; done
	for m in $(HARM_MODELS); do uv run --extra $(TORCH) python evaluate_guard.py --task harm --model $$m --n-harm $(N_HARM) || exit 1; done

run-all-gpu:  ## GPU 推奨の大型モデル × 全タスクを GPU で評価して results/ に保存
	for m in $(GPU_MODELS); do uv run --extra gpu python evaluate_guard.py --task pi --model $$m --device cuda || exit 1; done
	for m in $(GPU_MODELS); do uv run --extra gpu python evaluate_guard.py --task harm --model $$m --n-harm $(N_HARM) --device cuda || exit 1; done

clean:        ## ダウンロードしたデータ(datasets/)を削除
	rm -rf datasets
