# SensorLLM の推論／学習を Docker(GPU) + uv で実行する Makefile。
#
# 前提:
#   - NVIDIA GPU + ドライバ + nvidia-container-toolkit（docker --gpus all が使えること）
#   - HF_TOKEN を .env に設定しておくこと（未認証だと HF Xet DL が 403/503 になり得る）
#   - 公式リポジトリ(SensorLLM)・chronos-t5-base 調整・学習用メトリクスはイメージに焼き込み済み
#
# 典型フロー（Stage1 推論）:
#   make docker-build → make docker-model-download → make docker-prepare-data → make docker-stage1-predict
# 典型フロー（Stage2=HAR 分類。2 段学習が必要）:
#   make docker-build → make docker-model-download → make docker-prepare-train-data \
#     → make docker-stage1-train → make docker-stage2-train → make docker-stage2-predict
#
# 命名規約: コンテナ内で実行するタスクは docker- prefix。stage で predict/train が異なるため
#           docker-stage1-predict / docker-stage1-train / docker-stage2-train / docker-stage2-predict に分ける。

-include .env
export

IMAGE        ?= sensorllm-run:latest
HF_REPO      ?= 1EE1/SensorLLM-Stage1-Backup
CHRONOS_REPO ?= amazon/chronos-t5-base
DATASET      ?= mhealth
# 学習は cwd=/opt/SensorLLM で公式 train_mem.py を回すため、データ/モデルは絶対(/app)で渡す。
# /app は実行時にカレントをマウントする先。
CHRONOS      ?= /app/chronos_t5_base

# コンテナ実行: GPU 有効・カレントを /app にマウント・HF キャッシュ永続化・.env 注入
# （SensorLLM=/opt/SensorLLM・venv=/opt/uv-venv はイメージ内。/app 外なのでマウントに隠れない）
ENVFILE := $(if $(wildcard .env),--env-file .env,)
DOCKER_MOUNT = -v $(PWD):/app -v $(HOME)/.cache/huggingface:/root/.cache/huggingface
# 通常タスクは /app から実行（uv が pyproject.toml と venv=/opt/uv-venv を認識できる）。
DOCKER_RUN = docker run --rm --gpus all $(ENVFILE) $(DOCKER_MOUNT) -w /app $(IMAGE)
# 学習は公式 train_mem.py を使う。train.py が相対で ts_backbone.yaml / ../metrics を開くため
# cwd=/opt/SensorLLM で実行し、uv には --project /app で pyproject/venv の場所を教える。
DOCKER_TRAIN = docker run --rm --gpus all $(ENVFILE) $(DOCKER_MOUNT) -w /opt/SensorLLM $(IMAGE)

.PHONY: help docker-build clean docker-model-download docker-prepare-data docker-prepare-train-data \
        docker-stage1-predict docker-stage1-train docker-stage2-train docker-stage2-predict \
        docker-stage2-plot install lint format format-check

help:  ## タスク一覧を表示
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-26s\033[0m %s\n",$$1,$$2}'

# ---- 開発ツール（ローカル uv。lint / format） ----
install:  ## [ローカル] dev ツール（flake8/mypy/black/isort）を含む .venv を用意
	uv sync --extra dev

lint: install  ## [ローカル] flake8 / mypy で静的チェック
	uv run flake8 .
	uv run mypy .

format: install  ## [ローカル] black / isort で自動整形
	uv run black .
	uv run isort .

format-check: install  ## [ローカル] 整形済みか確認（CI 用・変更しない）
	uv run black --check .
	uv run isort --check-only .

docker-build:  ## Docker イメージをビルド（SensorLLM clone + uv sync + metrics 焼き込み）
	docker build -t $(IMAGE) .

docker-model-download:  ## [コンテナ] Stage1 ckpt と Chronos を取得（要 HF_TOKEN）
	$(DOCKER_RUN) sh -c "uv run --no-sync huggingface-cli download $(HF_REPO) --local-dir ckpt_1EE1 && \
	  uv run --no-sync huggingface-cli download $(CHRONOS_REPO) --local-dir chronos_t5_base"

docker-prepare-data:  ## [コンテナ] 実センサーデータ(MHealth)から 1 チャネル分の推論用サンプルを作る
	$(DOCKER_RUN) uv run --no-sync python prepare_sample.py

docker-prepare-train-data:  ## [コンテナ/CPU] 学習用データ+QA を生成（Stage1: ./data, Stage2: ./whole_data）
	$(DOCKER_RUN) sh -c "uv run --no-sync python mhealth_stage1_prep.py && \
	  uv run --no-sync python mhealth_stage2_prep.py"

# ---- Stage 1: センサー–言語アラインメント（トレンド説明） ----
STAGE1_MODEL ?= ./ckpt_1EE1
SAMPLE       ?= outputs/sample_c_acc_x.npy
CHANNEL      ?= c_acc_x
docker-stage1-predict: docker-prepare-data  ## [コンテナ/GPU] Stage1 推論（センサー信号のトレンドを自然言語説明）
	$(DOCKER_RUN) uv run --no-sync python stage1_predict.py \
	  --model-path $(STAGE1_MODEL) --chronos-path $(CHRONOS) \
	  --dataset $(DATASET) --channel $(CHANNEL) --input $(SAMPLE) \
	  --plot images/sensor_input.png --device cuda --dtype bfloat16

# base LLM は open な TinyLlama 等（gated を使うなら .env の HF_TOKEN に利用同意済みトークン）。
# 学習は公式 train_mem.py（flash-attn 使用。wheel をイメージに焼き込み済み）で回す。
# EPOCHS: 学習エポック数。SAVE_LIMIT: 保持する ckpt 数（多エポックで容量が溢れないよう既定 2）。
EPOCHS     ?= 1
SAVE_LIMIT ?= 2
LLM_PATH ?= TinyLlama/TinyLlama-1.1B-Chat-v1.0
OUT1     ?= /app/out_stage1
docker-stage1-train:  ## [コンテナ/GPU] Stage1 学習（アラインメント）。要 docker-prepare-train-data
	$(DOCKER_TRAIN) sh -c "uv run --no-sync --project /app torchrun --nproc_per_node=1 \
	  /opt/SensorLLM/sensorllm/train/train_mem.py \
	  --model_name_or_path $(LLM_PATH) --pt_encoder_backbone_ckpt $(CHRONOS) \
	  --tokenize_method 'StanNormalizeUniformBins' --dataset $(DATASET) \
	  --data_path /app/data/train/mhealth_train_data_stage1.pkl \
	  --eval_data_path /app/data/test/mhealth_test_data_stage1.pkl \
	  --qa_path /app/data/train/mhealth_train_qa_stage1.json \
	  --eval_qa_path /app/data/test/mhealth_test_qa_stage1.json \
	  --output_dir $(OUT1) --model_max_length 4096 --num_train_epochs $(EPOCHS) \
	  --per_device_train_batch_size 1 --per_device_eval_batch_size 1 \
	  --evaluation_strategy steps --save_strategy steps --save_total_limit $(SAVE_LIMIT) \
	  --learning_rate 2e-3 --weight_decay 0.0 --warmup_ratio 0.03 --lr_scheduler_type cosine \
	  --gradient_checkpointing True --bf16 True --fix_llm True --fix_ts_encoder True \
	  --model_type CasualLM --load_best_model_at_end True"

# ---- Stage 2: タスク適応チューニング（HAR 分類） ----
STAGE1_CKPT ?= /app/out_stage1
NUM_LABELS  ?= 12
OUT2        ?= /app/out_stage2
docker-stage2-train:  ## [コンテナ/GPU] Stage2 学習（HAR 分類）。要 Stage1 モデル + 学習用データ
	$(DOCKER_TRAIN) sh -c "uv run --no-sync --project /app torchrun --nproc_per_node=1 \
	  /opt/SensorLLM/sensorllm/train/train_mem.py \
	  --model_name_or_path $(STAGE1_CKPT) --pt_encoder_backbone_ckpt $(CHRONOS) \
	  --model_type 'SequenceClassification' --num_labels $(NUM_LABELS) --use_weighted_loss True \
	  --tokenize_method 'StanNormalizeUniformBins' --dataset $(DATASET) \
	  --data_path /app/whole_data/train/mhealth_train_data_stage2.pkl \
	  --eval_data_path /app/whole_data/test/mhealth_test_data_stage2.pkl \
	  --qa_path /app/whole_data/train/mhealth_train_qa_stage2_cls.json \
	  --eval_qa_path /app/whole_data/test/mhealth_test_qa_stage2_cls.json \
	  --output_dir $(OUT2) --model_max_length 4096 --num_train_epochs $(EPOCHS) \
	  --per_device_train_batch_size 1 --per_device_eval_batch_size 1 \
	  --evaluation_strategy epoch --save_strategy epoch --save_total_limit $(SAVE_LIMIT) \
	  --learning_rate 2e-3 --weight_decay 0.0 --warmup_ratio 0.03 --lr_scheduler_type cosine \
	  --gradient_checkpointing True --bf16 True --fix_llm True --fix_ts_encoder True --fix_cls_head False \
	  --metric_for_best_model f1_macro --greater_is_better True \
	  --preprocess_type 'smry+Q' --stage_2 True --shuffle True"

STAGE2_MODEL ?= ./out_stage2
NUM_SAMPLES  ?= 16
RESULTS      ?= outputs/stage2_predict_results.npz
docker-stage2-predict:  ## [コンテナ/GPU] Stage2 推論（HAR 分類）＋結果保存＋サンプル別プロット
	$(DOCKER_RUN) uv run --no-sync python stage2_predict.py \
	  --model-path $(STAGE2_MODEL) --chronos-path $(CHRONOS) \
	  --dataset $(DATASET) --num-labels $(NUM_LABELS) --num-samples $(NUM_SAMPLES) \
	  --save-results $(RESULTS) --plot-dir images/stage2_samples --device cuda --dtype bfloat16

docker-stage2-plot:  ## [コンテナ/CPU] 保存済み結果($(RESULTS))から推論なしで図だけ再生成
	$(DOCKER_RUN) uv run --no-sync python stage2_predict.py \
	  --from-results $(RESULTS) --plot-dir images/stage2_samples

clean:  ## 取得モデル・生成物を削除
	rm -rf ckpt_1EE1 chronos_t5_base $(OUT1) $(OUT2) outputs images/stage2_samples \
	  data whole_data MHEALTHDATASET
