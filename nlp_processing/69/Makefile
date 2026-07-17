# 系統(a) 数値直接入力による時系列異常検知。パッケージ管理は uv。API キーは .env(非 git 管理)。

-include .env
export

NAB_KEY ?= machine-temp
DOWNSAMPLE ?= 24
BASE_URL ?= https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL ?= gemini-3.5-flash
REASONING_EFFORT ?= low

.PHONY: install install-dev lint format format-check run clean help

help:         ## タスク一覧を表示
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n",$$1,$$2}'

install:      ## 依存を uv で仮想環境に同期
	uv sync

# ---- 開発ツール（lint / format） ----
install-dev:  ## dev ツール（flake8/mypy/black/isort）を含む .venv を用意
	uv sync --extra dev

lint: install-dev  ## flake8 / mypy で静的チェック
	uv run flake8 .
	uv run mypy .

format: install-dev  ## black / isort で自動整形
	uv run black .
	uv run isort .

format-check: install-dev  ## 整形済みか確認（CI 用・変更しない）
	uv run black --check .
	uv run isort --check-only .

run:          ## 数値直接入力で検知→NAB ラベルで評価（例: make run NAB_KEY=cpu）
	uv run python detect_numeric_llm.py --nab-key $(NAB_KEY) --downsample $(DOWNSAMPLE) \
	  --base-url $(BASE_URL) --llm-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

clean:        ## ダウンロードしたデータを削除
	rm -rf data
