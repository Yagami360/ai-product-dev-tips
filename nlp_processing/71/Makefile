# 異常検知 TSFM(TSPulse)+LLM の異常検知→レポート化 パイプライン
# パッケージ管理は uv。API キー等は .env（非 git 管理）に置く。

# .env があれば読み込んで環境変数として使う（OPENAI_API_KEY 等）
-include .env
export

# 対象センサー・説明層 LLM（.env や引数で上書き可）
NAB_KEY ?= machine-temp
BASE_URL ?= https://generativelanguage.googleapis.com/v1beta/openai/
LLM_MODEL ?= gemini-3.5-flash
REASONING_EFFORT ?= low

# TSPulse の異常検知はベースコンテキスト長(512)の 3〜4 倍（約 1,536〜2,048 点）以上を要求するため、既定は間引きなし
DOWNSAMPLE ?= 1

# TSPulse の anomaly_score は 0〜1 に正規化されるため、Chronos(nlp_processing/67) のような
# センサー別のしきい値調整は不要。既定 0.6 は公式 notebook 準拠（make run THRESHOLD=0.3 等で上書き可）。
THRESHOLD ?= 0.6

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

run:          ## 検知→レポート生成（例: make run NAB_KEY=cpu THRESHOLD=0.3）
	uv run python create_report.py --nab-key $(NAB_KEY) --threshold $(THRESHOLD) --downsample $(DOWNSAMPLE) \
	  --base-url $(BASE_URL) --llm-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

evaluate:     ## 生成レポートを LLM-as-judge で品質評価（例: make evaluate NAB_KEY=cpu）
	uv run python evaluate_report.py --report reports/$(NAB_KEY).md \
	  --base-url $(BASE_URL) --judge-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

clean:        ## ダウンロードしたデータ(datasets/)を削除
	rm -rf datasets
