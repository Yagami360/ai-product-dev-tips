# SensorLLM の推論／学習を Docker(GPU) + uv で実行する Makefile。
#
# 前提:
#   - NVIDIA GPU + ドライバ + nvidia-container-toolkit（docker --gpus all が使えること）
#   - HF_TOKEN を .env に設定しておくこと（未認証だと HF Xet DL が 403/503 になり得る）
#   - 公式リポジトリ(SensorLLM)と chronos-t5-base 調整はイメージ内に焼き込み済み（clone 不要）
#
# 典型フロー（推論）: make docker-build → make docker-model-download → make docker-prepare-data → make docker-stage1-predict
#
# 命名規約: コンテナ内で実行するタスクは docker- prefix。stage で predict/train が異なるため
#           docker-stage1-predict / docker-stage1-train / docker-stage2-train / docker-stage2-predict に分ける。

-include .env
export

IMAGE        ?= sensorllm-run:latest
HF_REPO      ?= 1EE1/SensorLLM-Stage1-Backup
CHRONOS_REPO ?= amazon/chronos-t5-base
DATASET      ?= mhealth
CHRONOS      ?= ./chronos_t5_base

# コンテナ実行: GPU 有効・カレントを /app にマウント・HF キャッシュ永続化・.env 注入
# （SensorLLM=/opt/SensorLLM・venv=/opt/uv-venv はイメージ内。/app 外なのでマウントに隠れない）
ENVFILE := $(if $(wildcard .env),--env-file .env,)
DOCKER_RUN = docker run --rm --gpus all $(ENVFILE) \
	-v $(PWD):/app \
	-v $(HOME)/.cache/huggingface:/root/.cache/huggingface \
	-w /app $(IMAGE)

.PHONY: help docker-build clean docker-model-download docker-prepare-data \
        docker-stage1-predict docker-stage1-train docker-stage2-train

help:  ## タスク一覧を表示
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-26s\033[0m %s\n",$$1,$$2}'

docker-build:  ## Docker イメージをビルド（SensorLLM clone + uv sync を焼き込み）
	docker build -t $(IMAGE) .

docker-model-download:  ## [コンテナ] Stage1 ckpt と Chronos を取得（要 HF_TOKEN）
	$(DOCKER_RUN) sh -c "uv run --no-sync huggingface-cli download $(HF_REPO) --local-dir ckpt_1EE1 && \
	  uv run --no-sync huggingface-cli download $(CHRONOS_REPO) --local-dir chronos_t5_base"

docker-prepare-data:  ## [コンテナ] 実センサーデータ(MHealth)から 1 チャネル分の推論用サンプルを作る
	$(DOCKER_RUN) uv run --no-sync python prepare_sample.py

# ---- Stage 1: センサー–言語アラインメント（トレンド説明） ----
STAGE1_MODEL ?= ./ckpt_1EE1
SAMPLE       ?= sample_c_acc_x.npy
CHANNEL      ?= c_acc_x
docker-stage1-predict: docker-prepare-data  ## [コンテナ/GPU] Stage1 推論（センサー信号のトレンドを自然言語説明）
	$(DOCKER_RUN) uv run --no-sync python stage1_predict.py \
	  --model-path $(STAGE1_MODEL) --chronos-path $(CHRONOS) \
	  --dataset $(DATASET) --channel $(CHANNEL) --input $(SAMPLE) \
	  --plot images/sensor_input.png --device cuda --dtype bfloat16

# base LLM は open な TinyLlama 等（gated を使うなら .env の HF_TOKEN に利用同意済みトークン）。
# データ/QA は要準備（README「学習」節）。パスは変数で上書き。
LLM_PATH ?= TinyLlama/TinyLlama-1.1B-Chat-v1.0
OUT1     ?= ./out_stage1
docker-stage1-train:  ## [コンテナ/GPU] Stage1 学習（アラインメント）。要データ/QA
	$(DOCKER_RUN) sh -c "uv run --no-sync torchrun --nproc_per_node=1 \
	  /opt/SensorLLM/sensorllm/train/train_mem.py \
	  --model_name_or_path $(LLM_PATH) --pt_encoder_backbone_ckpt $(CHRONOS) \
	  --tokenize_method 'StanNormalizeUniformBins' --dataset $(DATASET) \
	  --data_path $(TS_TRAIN) --eval_data_path $(TS_EVAL) \
	  --qa_path $(QA_TRAIN) --eval_qa_path $(QA_EVAL) \
	  --output_dir $(OUT1) --model_max_length 4096 --num_train_epochs 1 \
	  --per_device_train_batch_size 1 --per_device_eval_batch_size 1 \
	  --evaluation_strategy steps --save_strategy steps \
	  --learning_rate 2e-3 --weight_decay 0.0 --warmup_ratio 0.03 --lr_scheduler_type cosine \
	  --gradient_checkpointing True --bf16 True --fix_llm True --fix_ts_encoder True \
	  --model_type CasualLM --load_best_model_at_end True"

# ---- Stage 2: タスク適応チューニング（HAR 分類） ----
STAGE1_CKPT ?= ./out_stage1
NUM_LABELS  ?= 12
OUT2        ?= ./out_stage2
docker-stage2-train:  ## [コンテナ/GPU] Stage2 学習（HAR 分類）。要 Stage1 モデル + データ/QA
	$(DOCKER_RUN) sh -c "uv run --no-sync torchrun --nproc_per_node=1 \
	  /opt/SensorLLM/sensorllm/train/train_mem.py \
	  --model_name_or_path $(STAGE1_CKPT) --pt_encoder_backbone_ckpt $(CHRONOS) \
	  --model_type 'SequenceClassification' --num_labels $(NUM_LABELS) --use_weighted_loss True \
	  --tokenize_method 'StanNormalizeUniformBins' --dataset $(DATASET) \
	  --data_path $(TS_TRAIN) --eval_data_path $(TS_EVAL) \
	  --qa_path $(QA_TRAIN) --eval_qa_path $(QA_EVAL) \
	  --output_dir $(OUT2) --model_max_length 4096 --num_train_epochs 1 \
	  --per_device_train_batch_size 1 --per_device_eval_batch_size 1 \
	  --evaluation_strategy steps --save_strategy steps \
	  --learning_rate 2e-3 --weight_decay 0.0 --warmup_ratio 0.03 --lr_scheduler_type cosine \
	  --gradient_checkpointing True --bf16 True --fix_llm True --fix_ts_encoder True --fix_cls_head False \
	  --metric_for_best_model f1_macro --greater_is_better True \
	  --preprocess_type 'smry+Q' --stage_2 True --shuffle True"

clean:  ## 取得モデル・生成物を削除
	rm -rf ckpt_1EE1 chronos_t5_base $(OUT1) $(OUT2) sample_c_acc_x.npy images
