# 時系列基盤モデル(Chronos)+LLM の異常検知→レポート化 パイプライン
# パッケージ管理は uv。API キー等は .env（非 git 管理）に置く。

# .env があれば読み込んで環境変数として使う（OPENAI_API_KEY 等）
-include .env
export

# 対象センサー・説明層 LLM（.env や引数で上書き可）
NAB_KEY ?= machine-temp
BASE_URL ?= https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL ?= gemini-3.5-flash
REASONING_EFFORT ?= low

.PHONY: install install-dev lint format format-check run evaluate clean help

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

run:          ## 検知→レポート生成（例: make run NAB_KEY=cpu）
	uv run python create_report.py --device cpu --nab-key $(NAB_KEY) \
	  --base-url $(BASE_URL) --llm-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

evaluate:     ## 生成レポートを LLM-as-judge で品質評価（例: make evaluate NAB_KEY=cpu）
	uv run python evaluate_report.py --report reports/$(NAB_KEY).md \
	  --base-url $(BASE_URL) --judge-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

clean:        ## ダウンロードしたデータを削除
	rm -rf data
