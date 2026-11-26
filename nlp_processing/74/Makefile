MODE ?= session
MODEL ?= claude-sonnet-4-6
MAX_TURNS ?= 20
VIEW ?= 0
VIEW_PORT ?= 6080
VIEW_ENABLED := $(if $(filter 1,$(VIEW))$(filter manual,$(MODE)),1)
VIEW_ONLY := $(if $(filter manual,$(MODE)),0,1)

export MODE MODEL MAX_TURNS VIEW_PORT
export TIP74_MESSAGE := $(or $(value MESSAGE),$(value MEESAGE))
unexport MESSAGE MEESAGE

.PHONY: help setup install run send-message send-messgae stop

help:  ## タスク一覧を表示
	@awk 'BEGIN { FS=":.*## " } /^[a-z0-9-]+:.*## / { printf "  %-18s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

setup:  ## .env が無ければ .env.example から作成
	@if [ ! -e .env ]; then (umask 077; set -C; cat .env.example > .env); fi

install:  ## Linux デスクトップと uv の Python 環境を含むイメージをビルド
	docker compose build desktop

ifeq ($(MODE),session)
run:  ## ブラウザで閲覧できる Linux 画面を起動（VIEW_PORT）
	docker compose up -d --wait desktop-session
	@printf '%s\n' "noVNC http://127.0.0.1:$$VIEW_PORT/vnc.html?autoconnect=1&view_only=1&resize=scale"
else
run:
	@set -eu; \
	mkdir -p "out/desktop-$$MODE"; \
	run_dir=$$(mktemp -d "out/desktop-$$MODE/run.XXXXXXXX"); \
	container="computer-use-desktop-$${run_dir##*/}"; \
	project="computer-use-desktop-run-$$(printf '%s' "$${run_dir##*.}" | tr '[:upper:]' '[:lower:]')"; \
	trap 'docker rm -f "$$container" >/dev/null 2>&1 || true; docker compose -p "$$project" down >/dev/null 2>&1 || true' EXIT; \
	trap 'exit 130' INT; \
	trap 'exit 143' TERM; \
	set --; \
	if [ "$(VIEW_ENABLED)" = 1 ]; then \
		set -- -p "127.0.0.1:$$VIEW_PORT:6080"; \
		printf '%s\n' "noVNC http://127.0.0.1:$$VIEW_PORT/vnc.html?autoconnect=1&view_only=$(VIEW_ONLY)&resize=scale"; \
	fi; \
	if [ "$$MODE" = manual ]; then set -- "$$@" -e NOVNC_PASSWORD; fi; \
	status=0; \
	docker compose -p "$$project" run -T --name "$$container" "$$@" \
		$(if $(filter claude,$(MODE)),,-e ANTHROPIC_API_KEY=) desktop \
		--mode "$$MODE" --model "$$MODEL" --max-turns "$$MAX_TURNS" \
		--out-dir /tmp/run-output $(if $(VIEW_ENABLED),--view) || status=$$?; \
	if ! docker cp "$$container:/tmp/run-output/." "$$run_dir/" && [ "$$status" -eq 0 ]; then status=1; fi; \
	printf '%s\n' "出力先 $$run_dir"; \
	exit "$$status"
endif

send-message:  ## 起動済みの Linux 画面で Claude に日本語の指示を送る
	@set -eu; \
	status=0; \
	result=$$(printf '%s' "$$TIP74_MESSAGE" | docker compose --profile session exec -T desktop-session /app/.venv/bin/python /app/run.py --send-message) || status=$$?; \
	if [ -n "$$result" ]; then \
		printf '%s\n' "$$result"; \
		mkdir -p out/desktop-claude; \
		run_dir=$$(mktemp -d out/desktop-claude/run.XXXXXXXX); \
		docker compose --profile session cp desktop-session:/tmp/run-output/. "$$run_dir/"; \
		printf '%s\n' "出力先 $$run_dir"; \
	fi; \
	exit "$$status"

send-messgae: send-message

stop:  ## ブラウザに表示した Linux 画面を終了
	docker compose --profile session down
