# クラウドのマネージドガードレールサービスの日本語実測比較
# パッケージ管理は uv。各サービスの認証情報は環境変数で渡す（README 参照）。

TASK ?= pi
SERVICE ?= azure
N_HARM ?= 200
INTERVAL ?= 0
SERVICES ?= azure azure-docs model-armor

.PHONY: help install lint format format-check setup-model-armor setup-bedrock-guardrail run run-all clean

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

setup-model-armor:  ## Model Armor API を有効化し、評価用テンプレートを作成
	./setup_model_armor.sh

setup-bedrock-guardrail:  ## 評価用の Bedrock ガードレール（Standard tier）を作成し、ID を表示
	@./setup_bedrock_guardrail.sh

run:          ## 1 サービスを評価（例: make run TASK=harm SERVICE=model-armor）
	uv run python evaluate_guard.py --task $(TASK) --service $(SERVICE) --n-harm $(N_HARM) --interval $(INTERVAL)

run-all:      ## 指定サービス(SERVICES)× 全タスクを評価して results/ に保存
	for s in $(SERVICES); do for t in pi harm; do \
		uv run python evaluate_guard.py --task $$t --service $$s --n-harm $(N_HARM) --interval $(INTERVAL) || exit 1; \
	done; done

clean:        ## ダウンロードしたデータ(datasets/)を削除
	rm -rf datasets
