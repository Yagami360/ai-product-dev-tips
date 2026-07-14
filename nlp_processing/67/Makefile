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

.PHONY: install run evaluate clean help

help:       ## タスク一覧を表示
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

install:    ## 依存を uv で仮想環境に同期
	uv sync

run:        ## 検知→レポート生成（例: make run NAB_KEY=cpu）
	uv run python create_report.py --device cpu --nab-key $(NAB_KEY) \
	  --base-url $(BASE_URL) --llm-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

evaluate:   ## 生成レポートを LLM-as-judge で品質評価（例: make evaluate NAB_KEY=cpu）
	uv run python evaluate_report.py --report reports/$(NAB_KEY).md \
	  --base-url $(BASE_URL) --judge-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

clean:      ## ダウンロードしたデータを削除
	rm -rf data
