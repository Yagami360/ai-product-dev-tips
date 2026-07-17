# 系統(b) 画像化→VLM による時系列異常検知。パッケージ管理は uv。API キーは .env(非 git 管理)。

-include .env
export

NAB_KEY ?= machine-temp
DOWNSAMPLE ?= 24
BASE_URL ?= https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL ?= gemini-3.5-flash
REASONING_EFFORT ?= low

.PHONY: install lint format format-check download-nab-dataset run evaluate clean help

help:         ## タスク一覧を表示
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n",$$1,$$2}'

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

# 取得対象（既定 all = プリセット全 6 センサー。単体なら make download-nab-dataset DOWNLOAD_KEY=cpu）
DOWNLOAD_KEY ?= all
download-nab-dataset:  ## NAB の実センサーデータ・正解ラベルを datasets/nab へ取得（既定は全 6 センサー）
	uv run python download_dataset.py --nab-key $(DOWNLOAD_KEY)

run:          ## 画像化→VLM で検知→NAB ラベルで評価（例: make run NAB_KEY=cpu）
	uv run python detect_vlm_image.py --nab-key $(NAB_KEY) --downsample $(DOWNSAMPLE) \
	  --base-url $(BASE_URL) --llm-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

evaluate:     ## 生成レポートを LLM-as-judge で品質評価（例: make evaluate NAB_KEY=cpu）
	uv run python evaluate_report.py --report reports/$(NAB_KEY).md \
	  --base-url $(BASE_URL) --judge-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

clean:        ## ダウンロードしたデータ(datasets/)を削除
	rm -rf datasets
