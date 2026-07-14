# 系統(b) 画像化→VLM による時系列異常検知。パッケージ管理は uv。API キーは .env(非 git 管理)。

-include .env
export

NAB_KEY ?= machine-temp
DOWNSAMPLE ?= 24
BASE_URL ?= https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL ?= gemini-3.5-flash
REASONING_EFFORT ?= low

.PHONY: install run clean help

help:      ## タスク一覧を表示
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

install:   ## 依存を uv で仮想環境に同期
	uv sync

run:       ## 画像化→VLM で検知→NAB ラベルで評価（例: make run NAB_KEY=cpu）
	uv run python detect_vlm_image.py --nab-key $(NAB_KEY) --downsample $(DOWNSAMPLE) \
	  --base-url $(BASE_URL) --llm-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

clean:     ## ダウンロードしたデータを削除
	rm -rf data
