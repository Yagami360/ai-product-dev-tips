PYTHON_VERSION ?= 3.12
SHIFT_LAYOUT ?= 0
HOST_UID ?= $(shell id -u)
HOST_GID ?= $(shell id -g)
RUN = uv run --locked --python "$(PYTHON_VERSION)"
DOTENV = $(if $(wildcard .env),--env-file .env,--no-env-file)
LAYOUT = $(if $(filter 1,$(SHIFT_LAYOUT)),--shift-layout)

export HOST_UID HOST_GID

.PHONY: help setup install install-local codegen replay-recorded replay manual

help:  ## タスク一覧を表示
	@awk 'BEGIN { FS=":.*## " } /^[a-z0-9-]+:.*## / { printf "  %-18s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

setup:  ## .env が無ければ .env.example から作成
	@if [ ! -e .env ]; then (umask 077; set -C; cat .env.example > .env); fi

install:  ## 自動再実行用の Chromium イメージをビルド
	docker compose build replay

install-local:  ## 実演と引き継ぎ用にホストの Python 環境と Chromium を用意
	uv sync --locked --python "$(PYTHON_VERSION)"
	$(RUN) python -m playwright install chromium

codegen:  ## ホストでブラウザ操作を記録して recorded.py を生成
	@sandbox_url=$$($(RUN) python -B -c 'from replay import SANDBOX_URL; print(SANDBOX_URL)') && \
		$(RUN) python -m playwright codegen --target=python --output recorded.py "$$sandbox_url"

replay-recorded:  ## ホストで recorded.py を再生
	@test -f recorded.py || { printf '%s\n' '先に make codegen で操作を記録してください。' >&2; exit 1; }
	$(RUN) python recorded.py

replay:  ## コンテナで入力・送信・完了判定（TICKET_ID、SHIFT_LAYOUT）
	docker compose run --rm replay $(LAYOUT)

manual:  ## ホストで人に送信操作を引き継ぐ（TICKET_ID、SHIFT_LAYOUT）
	$(RUN) $(DOTENV) python replay.py --manual $(LAYOUT)
