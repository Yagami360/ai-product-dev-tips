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

# 異常判定スコアのしきい値は「予測区間からの逸脱を band 幅で正規化した値」なので、
# センサーの周期性・ノイズ特性でスコアの出方が大きく変わる（実測のスコア最大値は
# ambient-temp が 1.22、network が 660）。一律 1.5 だと ambient-temp / traffic-occupancy は
# 検知 0 件になるため、センサーごとに既定値を持たせる（make run THRESHOLD=0.3 等で上書き可）。
THRESHOLD_machine-temp      ?= 1.5
THRESHOLD_ambient-temp      ?= 0.8
THRESHOLD_cpu               ?= 0.5
THRESHOLD_traffic-speed     ?= 1.5
THRESHOLD_traffic-occupancy ?= 0.6
THRESHOLD_network           ?= 1.5
THRESHOLD ?= $(or $(THRESHOLD_$(NAB_KEY)),1.5)

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

run:          ## 検知→レポート生成（例: make run NAB_KEY=cpu）
	uv run python create_report.py --device cpu --nab-key $(NAB_KEY) --threshold $(THRESHOLD) \
	  --base-url $(BASE_URL) --llm-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

evaluate:     ## 生成レポートを LLM-as-judge で品質評価（例: make evaluate NAB_KEY=cpu）
	uv run python evaluate_report.py --report reports/$(NAB_KEY).md \
	  --base-url $(BASE_URL) --judge-model $(LLM_MODEL) --reasoning-effort $(REASONING_EFFORT)

clean:        ## ダウンロードしたデータ(datasets/)を削除
	rm -rf datasets
