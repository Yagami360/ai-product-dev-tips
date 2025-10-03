# uvを使用したMCPサーバーの管理用Makefile

.PHONY: install setup-cursor run lint format format-check

# uvでの依存関係インストール
install:
	uv lock --upgrade
	uv sync --extra dev

# Cursor MCP 設定の適用
setup-cursor:
	@echo "⚙️  Cursor MCP設定を適用中..."
	@CURSOR_CONFIG_DIR="$(HOME)/.cursor"
	@mkdir -p "$$CURSOR_CONFIG_DIR"
	@if [ -f "$$CURSOR_CONFIG_DIR/mcp_config.json" ]; then \
		cp "$$CURSOR_CONFIG_DIR/mcp_config.json" \
		   "$$CURSOR_CONFIG_DIR/mcp_config.json.backup.$$(date +%Y%m%d_%H%M%S)"; \
		echo "   既存設定をバックアップしました"; \
	fi
	@cp cursor_mcp_config.json "$$CURSOR_CONFIG_DIR/mcp_config.json"
	@echo "   Cursor MCP設定を更新しました"
	@echo "   設定ファイル: $$CURSOR_CONFIG_DIR/mcp_config.json"

# MCPサーバー実行
run: install
	@echo "🧪 MCPサーバー起動中..."
	@echo "Ctrl+C で停止できます"
	uv run python mcp_server.py

# Run code linting
lint: install
	uv run flake8 .
	uv run mypy .

# Run code formatting
format: install
	uv run black .
	uv run isort .

# Run code formatting check
format-check: install
	uv run black --check .
	uv run isort --check-only .
