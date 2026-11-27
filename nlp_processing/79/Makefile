export DECISION_MESSAGE := $(value MESSAGE)
unexport MESSAGE

.PHONY: help setup install run evaluate

help:  ## タスク一覧を表示
	@awk 'BEGIN { FS=":.*## " } /^[a-z0-9-]+:.*## / { printf "  %-12s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

setup:  ## .env が無ければ .env.example から作成
	@if [ ! -e .env ]; then (umask 077; set -C; cat .env.example > .env); fi

install:  ## uv で Python 環境を同期
	uv sync --locked

run:  ## 問い合わせを判定して JSON を表示（入力は MESSAGE で変更）
	@uv run --locked $(if $(wildcard .env),--env-file .env) python run.py

evaluate:  ## サンプル 4 件で Choice のみと 2 段方式を比較
	@uv run --locked $(if $(wildcard .env),--env-file .env) python run.py --evaluate
