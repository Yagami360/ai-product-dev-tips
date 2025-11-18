.PHONY: install train lint format format-check

# Install dependencies
install:
	uv lock --upgrade
	uv sync --extra dev

# train LLM model
train: install
	uv run python train.py

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
