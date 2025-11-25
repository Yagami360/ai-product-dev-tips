# export CUDA_VISIBLE_DEVICES=0
export CUDA_VISIBLE_DEVICES=8,9

export EXPER_NAME=qwen2-7b-to-qwen2-0.5b-logit-distill-$(shell date +%Y%m%d)
export TEACHER_MODEL_NAME=Qwen/Qwen2-7B-Instruct
export STUDENT_MODEL_NAME=Qwen/Qwen2-0.5B-Instruct

.PHONY: install-uv install train train-nohup train-nohup-poweroff predict-teacher predict-student tensorboard lint format format-check

# Install
install-uv:
	@if command -v uv > /dev/null 2>&1; then \
		echo "uv is already installed. Skipping installation."; \
		echo "uv version: $$(uv --version)"; \
	else \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "uv installed successfully."; \
		echo "Please restart your shell or run: source ~/.bashrc"; \
	fi

install:
	uv lock --upgrade
	@if command -v nvidia-smi > /dev/null 2>&1; then \
		echo "GPU detected. Installing GPU dependencies..."; \
		uv sync --extra dev --extra gpu; \
	else \
		echo "No GPU detected. Skipping GPU dependencies installation."; \
		uv sync --extra dev; \
	fi

# Train LLM model
train: install
	rm -rf outputs/${EXPER_NAME}
	uv run python train.py \
		--exper_name ${EXPER_NAME} \
		--teacher_model_name ${TEACHER_MODEL_NAME} \
		--student_model_name ${STUDENT_MODEL_NAME}

train-nohup: install
	rm -rf outputs/${EXPER_NAME}
	nohup uv run python train.py \
		--exper_name ${EXPER_NAME} \
		--teacher_model_name ${TEACHER_MODEL_NAME} \
		--student_model_name ${STUDENT_MODEL_NAME} > ${EXPER_NAME}.out &

train-nohup-poweroff: install
	nohup bash train_poweroff.sh > ${EXPER_NAME}.out &

# Predict trained model
predict-teacher:
	@echo "Predicting by pre-trained teacher model ..."
	uv run python predict.py \
		--model_name ${TEACHER_MODEL_NAME} \
		--teacher_model_name ${TEACHER_MODEL_NAME} \
		--output_dir outputs/${EXPER_NAME}

predict-student:
	@echo "Predicting by pre-trained student model ..."
	uv run python predict.py \
		--model_name ${STUDENT_MODEL_NAME} \
		--teacher_model_name ${TEACHER_MODEL_NAME} \
		--output_dir outputs/${EXPER_NAME}

predict-distilled-student:
	@echo "Predicting by distilled student model ..."
	uv run python predict.py \
		--model_name outputs/${EXPER_NAME}/checkpoint-final \
		--teacher_model_name ${TEACHER_MODEL_NAME} \
		--output_dir outputs/${EXPER_NAME}

# Run tensorboard
tensorboard:
	uv run tensorboard --logdir outputs/${EXPER_NAME}/logs

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
