.PHONY: install-uv install train lint format format-check

export EXPER_NAME=qwen2-7b-to-qwen2-0.5b-distill-20251119

install-uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	source ~/.bashrc
	uv --version

# Install dependencies
install:
	uv lock --upgrade
	@if command -v nvidia-smi > /dev/null 2>&1; then \
		echo "GPU detected. Installing bitsandbytes..."; \
		uv sync --extra dev --extra gpu; \
	else \
		echo "No GPU detected. Skipping bitsandbytes installation."; \
		uv sync --extra dev; \
	fi

# train LLM model
train: install
	rm -rf outputs/${EXPER_NAME}
	uv run python train.py --exper_name ${EXPER_NAME}

train-nohup-poweroff: install
	nohup bash train_poweroff.sh > ${EXPER_NAME}.out &

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
