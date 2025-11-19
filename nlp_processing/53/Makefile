.PHONY: install-uv install train lint format format-check infer

export EXPER_NAME=qwen2-7b-to-qwen2-0.5b-distill-20251119
export TEACHER_MODEL_NAME=Qwen/Qwen2-7B-Instruct
export STUDENT_MODEL_NAME=Qwen/Qwen2-0.5B-Instruct

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
	uv run python train.py --exper_name ${EXPER_NAME} --teacher_model_name ${TEACHER_MODEL_NAME} --student_model_name ${STUDENT_MODEL_NAME}

train-nohup-poweroff: install
	nohup bash train_poweroff.sh > ${EXPER_NAME}.out &

# predict trained model
predict:
	@echo "Predicting by pre-trained teacher model ..."
	uv run python predict.py \
		--model_name ${TEACHER_MODEL_NAME} \
		--teacher_model_name ${TEACHER_MODEL_NAME} \
		--output_dir outputs/${EXPER_NAME}

	@echo "Predicting by distilled student model ..."
	uv run python predict.py \
		--model_name outputs/${EXPER_NAME}/checkpoint-final \
		--teacher_model_name ${TEACHER_MODEL_NAME} \
		--output_dir outputs/${EXPER_NAME}
	# uv run python predict.py \
	# 	--model_name outputs/qwen2-7b-to-qwen2-0.5b-distill-debug-20251119/checkpoint-2000 \
	# 	--teacher_model_name ${TEACHER_MODEL_NAME} \
	# 	--output_dir outputs/qwen2-7b-to-qwen2-0.5b-distill-debug-20251119

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
