# ローカルガードレールモデルの日本語 CPU 実測比較
# パッケージ管理は uv。Ollama 系モデルは事前に `make pull-ollama-models` で取得する。

TASK ?= pi
MODEL ?= horizon-pi-guard
N_HARM ?= 200

PI_MODELS := horizon-pi-guard protectai-deberta-pi qwen3guard-gen-0.6b llama-guard3-1b shieldgemma-2b granite3-guardian-2b
HARM_MODELS := qwen3guard-gen-0.6b llama-guard3-1b shieldgemma-2b granite3-guardian-2b
OLLAMA_MODELS := llama-guard3:1b shieldgemma:2b granite3-guardian:2b

.PHONY: help install lint format format-check pull-ollama-models run run-all clean

help:         ## タスク一覧を表示
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-20s\033[0m %s\n",$$1,$$2}'

install:      ## 依存(+dev ツール)を uv で仮想環境に同期
	uv sync --extra dev

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

run:          ## 1 モデルを評価（例: make run TASK=harm MODEL=llama-guard3-1b）
	uv run python evaluate_guard.py --task $(TASK) --model $(MODEL) --n-harm $(N_HARM)

run-all:      ## 全モデル × 全タスクを評価して results/ に保存
	for m in $(PI_MODELS); do uv run python evaluate_guard.py --task pi --model $$m || exit 1; done
	for m in $(HARM_MODELS); do uv run python evaluate_guard.py --task harm --model $$m --n-harm $(N_HARM) || exit 1; done

clean:        ## ダウンロードしたデータ(datasets/)を削除
	rm -rf datasets
