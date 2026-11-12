# クラウドのマネージドガードレールサービスの日本語実測比較
# パッケージ管理は uv。各サービスの認証情報は .env に書く（.env.example 参照）。

TASK ?= pi
SERVICE ?= azure
N_HARM ?= 200
INTERVAL ?= 0
SERVICES ?= azure azure-docs model-armor

# 認証情報などは .env から読み込み、スクリプトに環境変数として渡す（.env.example 参照）
-include .env
export

.PHONY: help install setup lint format format-check setup-azure setup-gcp setup-aws cleanup-azure cleanup-gcp cleanup-aws run run-all clean

help:         ## タスク一覧を表示
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-15s\033[0m %s\n",$$1,$$2}'

install:      ## 依存(+dev ツール)を uv で仮想環境に同期
	uv sync --extra dev

setup:        ## .env が無ければ .env.example から作成（既にあれば何もしない）
	@if [ -f .env ]; then echo ".env は既にあります"; else cp .env.example .env && echo ".env を作成しました。値を埋めてください"; fi

lint: install  ## flake8 / mypy で静的チェック
	uv run flake8 .
	uv run mypy .

format: install  ## black / isort で自動整形
	uv run black .
	uv run isort .

format-check: install  ## 整形済みか確認（CI 用・変更しない）
	uv run black --check .
	uv run isort --check-only .

setup-azure:  ## 評価用の Azure AI Content Safety リソース（F0）を作成し、.env 形式で表示
	@./tools/setup_azure_content_safety.sh

setup-gcp:  ## Model Armor API を有効化し、評価用テンプレートを作成
	./tools/setup_gcp_model_armor.sh

setup-aws:  ## 評価用の Bedrock ガードレール（Standard tier）を作成し、ID を表示
	@./tools/setup_aws_bedrock_guardrail.sh

cleanup-azure:  ## 評価用の Azure リソースグループを削除し、Content Safety リソースを purge
	./tools/cleanup_azure_content_safety.sh

cleanup-gcp:  ## 評価用の Model Armor テンプレートを削除
	./tools/cleanup_gcp_model_armor.sh

cleanup-aws:  ## 評価用の Bedrock ガードレールを削除
	./tools/cleanup_aws_bedrock_guardrail.sh

run:          ## 1 サービスを評価（例: make run TASK=harm SERVICE=model-armor）
	uv run python evaluate_guard.py --task $(TASK) --service $(SERVICE) --n-harm $(N_HARM) --interval $(INTERVAL)

run-all:      ## 指定サービス(SERVICES)× 全タスクを評価して results/ に保存
	for s in $(SERVICES); do for t in pi harm; do \
		uv run python evaluate_guard.py --task $$t --service $$s --n-harm $(N_HARM) --interval $(INTERVAL) || exit 1; \
	done; done

clean:        ## ダウンロードしたデータ(datasets/)を削除
	rm -rf datasets
