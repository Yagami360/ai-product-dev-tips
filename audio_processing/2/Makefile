PYTHON_VERSION ?= 3.12
SPEECH ?= ./speech-cpp/speech
AUDIO ?= sample.wav
OUTPUT ?=
TEXT ?= 設備の状態を確認してください。
MODEL ?= reazonspeech-v2:q4_k
TTS_MODEL ?= qwen3-tts-0.6b:q4_k
THREADS ?= 4
VOICEVOX_URL ?= http://127.0.0.1:50021
MOSHI_PYTHON ?= .venv-moshi/bin/python

LFM2_DIR := _tmp/lfm2
LFM2_WEIGHTS := LFM2.5-Audio-1.5B-JP-Q4_0.gguf
LFM2_SOURCE := https://huggingface.co/LiquidAI/LFM2.5-Audio-1.5B-JP-GGUF/resolve/64b96718b341dbd5650f9e85627cecdcbd4ac61b
LFM3_DIR := _tmp/lfm3
LFM3_SOURCE := https://huggingface.co/LiquidAI/LFM3-Audio-2B-GGUF/resolve/39670cb5c42e9c4bfe046519ba7ffbe47f9552ad
LFM3_WEIGHTS := LFM3-Audio-2B-Q4_K_M.gguf
LFM3_PROJECTOR := mmproj-LFM3-Audio-2B-Q8_0.gguf
LLAMA_BIN ?= $(LFM3_DIR)/llama-b11960/llama
LLAMA_TTS ?= $(LFM3_DIR)/llama-b11960/llama-tts

export SPEECH AUDIO OUTPUT TEXT MODEL TTS_MODEL THREADS VOICEVOX_URL LLAMA_BIN LLAMA_TTS

.PHONY: help setup install install-speech install-moshi install-moshi-cpu download-speech-models download-voicevox download-lfm2 download-lfm3 download-moshi asr tts serve-voicevox lfm2-dialogue lfm3-asr lfm3-tts evaluate-asr evaluate-tts gemini-asr gemini-tts gemini-live moshi-web moshi-wav moshi-wav-cpu
.PHONY: download-qwen-q8 evaluate-qwen-q8
.PHONY: openai-asr openai-tts openai-dialogue

help:  ## タスク一覧を表示
	@awk 'BEGIN { FS=":.*## " } /^[a-z0-9-]+:.*## / { printf "  %-18s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

setup:  ## .env が無ければ .env.example から作成
	@if [ ! -e .env ]; then (umask 077; set -C; cat .env.example > .env); fi

.venv/bin/python:
	uv venv --python $(PYTHON_VERSION) .venv

install: .venv/bin/python  ## Gemini API と OpenAI API の依存をインストール
	uv pip install --python .venv/bin/python -r requirements.txt

install-speech:  ## speech.cpp v0.11.0 の Linux x86-64 CPU 版を展開
	@set -eu; \
	base=https://github.com/nyosegawa/speech.cpp/releases/download/v0.11.0; \
	archive=speech-0.11.0-linux-x64-cpu.zip; \
	mkdir -p _tmp; \
	curl -fsSL "$$base/$$archive" -o "_tmp/$$archive"; \
	curl -fsSL "$$base/SHA256SUMS" -o _tmp/SHA256SUMS; \
	(cd _tmp && sha256sum --ignore-missing -c SHA256SUMS); \
	unzip -oq "_tmp/$$archive" -d speech-cpp

.venv-moshi/bin/python:
	uv venv --python $(PYTHON_VERSION) .venv-moshi

install-moshi: .venv-moshi/bin/python  ## LLM-jp-Moshi-v1 の依存をインストール
	uv pip install --python .venv-moshi/bin/python -r requirements-moshi.txt

.venv-moshi-cpu/bin/python:
	uv venv --python $(PYTHON_VERSION) .venv-moshi-cpu

install-moshi-cpu: .venv-moshi-cpu/bin/python  ## Moshi の録音ファイル推論用に CPU 版 PyTorch を用意
	uv pip install --python .venv-moshi-cpu/bin/python --index-url https://download.pytorch.org/whl/cpu 'torch==2.6.0+cpu'
	uv pip install --python .venv-moshi-cpu/bin/python -r requirements-moshi.txt

download-speech-models:  ## ReazonSpeech と Qwen3-ASR（文字起こし）/ TTS（読み上げ）の 0.6B・1.7B を取得
	"$$SPEECH" pull reazonspeech-v2:q4_k qwen3-asr-0.6b:q4_k qwen3-asr-1.7b:q4_k \
		qwen3-tts-0.6b:q4_k qwen3-tts-1.7b:q4_k

download-qwen-q8:  ## Qwen3-ASR（文字起こし）/ TTS（読み上げ）1.7B の Q8_0 版を取得
	"$$SPEECH" pull qwen3-asr-1.7b:q8_0 qwen3-tts-1.7b:q8_0

download-voicevox:  ## VOICEVOX の CPU イメージを取得
	docker pull voicevox/voicevox_engine:cpu-latest

download-lfm2:  ## LFM2.5-Audio-1.5B-JP のランナーと日本語 GGUF を取得
	mkdir -p '$(LFM2_DIR)'
	set -eu; cd '$(LFM2_DIR)'; \
	if [ ! -x llama-liquid-audio-ubuntu-x64/llama-liquid-audio-cli ]; then \
		curl -fsSL '$(LFM2_SOURCE)/runners/llama-liquid-audio-ubuntu-x64.zip' -o runner.zip; \
		unzip -oq runner.zip; \
	fi; \
	for file in $(LFM2_WEIGHTS) mmproj-$(LFM2_WEIGHTS) vocoder-$(LFM2_WEIGHTS) tokenizer-$(LFM2_WEIGHTS); do \
		if [ ! -s "$$file" ]; then curl -fsSL '$(LFM2_SOURCE)/'"$$file" -o "$$file.part" && mv "$$file.part" "$$file" || exit 1; fi; \
	done

download-lfm3:  ## llama.cpp b11960 と LFM3-Audio-2B の GGUF を取得
	mkdir -p '$(LFM3_DIR)'
	set -eu; cd '$(LFM3_DIR)'; \
	if [ ! -x llama-b11960/llama ]; then \
		curl -fsSL https://github.com/ggml-org/llama.cpp/releases/download/b11960/llama-b11960-bin-ubuntu-x64.tar.gz -o runner.tar.gz; \
		tar -xzf runner.tar.gz; \
	fi; \
	for file in $(LFM3_WEIGHTS) $(LFM3_PROJECTOR); do \
		if [ ! -s "$$file" ]; then curl -fsSL '$(LFM3_SOURCE)/'"$$file" -o "$$file.part" && mv "$$file.part" "$$file" || exit 1; fi; \
	done

download-moshi:  ## LLM-jp-Moshi-v1 の重みとトークナイザーを Hugging Face キャッシュに取得
	"$(MOSHI_PYTHON)" -c 'from huggingface_hub import snapshot_download; print(snapshot_download("llm-jp/llm-jp-moshi-v1", allow_patterns=["model.safetensors", "tokenizer_spm_32k_3.model", "tokenizer-e351c8d8-checkpoint125.safetensors"]))'

asr:  ## speech.cpp で ASR（文字起こし）（AUDIO、MODEL）
	@set --; case "$$MODEL" in qwen3-asr-*) set -- --language ja ;; esac; \
	"$$SPEECH" asr "$$MODEL" --device cpu --threads "$$THREADS" "$$@" "$$AUDIO"

tts:  ## Qwen3-TTS で TTS（読み上げ）（TTS_MODEL、TEXT、OUTPUT）
	"$$SPEECH" tts "$$TTS_MODEL" --device cpu --threads "$$THREADS" \
		--language ja --voice ono_anna --seed 42 -o "$${OUTPUT:-sample.wav}" "$$TEXT"

serve-voicevox:  ## VOICEVOX ENGINE の CPU 版を起動
	docker run --rm -p 127.0.0.1:50021:50021 voicevox/voicevox_engine:cpu-latest

lfm2-dialogue:  ## LFM2.5-Audio 日本語版で録音に応答（AUDIO、OUTPUT）
	@set -eu; run_dir=$$(mktemp -d '$(LFM2_DIR)/run.XXXXXX'); \
	ffmpeg -v error -i "$$AUDIO" -ar 24000 -ac 1 -c:a pcm_s16le "$$run_dir/input.wav"; \
	docker run --rm --network none --user "$$(id -u):$$(id -g)" \
		-v "$(abspath $(LFM2_DIR)):/models:ro" -v "$(CURDIR)/$$run_dir:/audio" -w /models ubuntu:24.04 \
		./llama-liquid-audio-ubuntu-x64/llama-liquid-audio-cli \
		-m '$(LFM2_WEIGHTS)' -mm 'mmproj-$(LFM2_WEIGHTS)' \
		-mv 'vocoder-$(LFM2_WEIGHTS)' --tts-speaker-file 'tokenizer-$(LFM2_WEIGHTS)' \
		--device none -ngl 0 -t "$$THREADS" -s 42 -n 128 -sys 'Respond with interleaved text and audio.' \
		--audio /audio/input.wav --output /audio/output.wav; \
	mv "$$run_dir/output.wav" "$${OUTPUT:-lfm-reply.wav}"

lfm3-asr:  ## LFM3-Audio-2B で日本語の ASR（文字起こし）（AUDIO）
	"$$LLAMA_BIN" cli -m '$(LFM3_DIR)/$(LFM3_WEIGHTS)' -mm '$(LFM3_DIR)/$(LFM3_PROJECTOR)' \
		--device none -ngl 0 -t "$$THREADS" -c 2048 --no-warmup --single-turn --no-display-prompt --simple-io \
		-n 128 --audio "$$AUDIO" -sys 'Perform ASR in Japanese.' -p '<__media__>' --temp 0

lfm3-tts:  ## LFM3-Audio-2B で日本語の TTS（読み上げ）（TEXT、OUTPUT）
	"$$LLAMA_TTS" -m '$(LFM3_DIR)/$(LFM3_WEIGHTS)' -mm '$(LFM3_DIR)/$(LFM3_PROJECTOR)' \
		--device none -ngl 0 -t "$$THREADS" -s 42 --tts-lang ja --tts-voice female \
		-p "$$TEXT" -o "$${OUTPUT:-lfm3-tts.wav}"

evaluate-asr:  ## 日本語朗読 5 件で speech.cpp の ASR（文字起こし）を比較
	uv run --no-project --python $(PYTHON_VERSION) python evaluate_cpu.py asr \
		--speech "$$SPEECH" --threads "$$THREADS"

evaluate-tts:  ## VOICEVOX と Qwen3-TTS の TTS（読み上げ）を再転写して比較
	uv run --no-project --python $(PYTHON_VERSION) python evaluate_cpu.py tts \
		--speech "$$SPEECH" --threads "$$THREADS" --voicevox-url "$$VOICEVOX_URL"

evaluate-qwen-q8:  ## Qwen3 1.7B Q8_0 で公開朗読の転写と短文の読み上げを評価
	uv run --no-project --python $(PYTHON_VERSION) python evaluate_cpu.py asr --qwen-q8 \
		--speech "$$SPEECH" --threads "$$THREADS"
	uv run --no-project --python $(PYTHON_VERSION) python evaluate_cpu.py tts --qwen-q8 \
		--speech "$$SPEECH" --threads "$$THREADS"

gemini-asr:  ## Gemini で ASR（文字起こし）（AUDIO）
	.venv/bin/python run.py asr -- "$$AUDIO"

gemini-tts:  ## Gemini で TTS（読み上げ）（TEXT、OUTPUT）
	.venv/bin/python run.py tts --output "$${OUTPUT:-gemini-tts.wav}" -- "$$TEXT"

gemini-live:  ## Gemini Live で設備を照会（16 kHz WAV の AUDIO、OUTPUT）
	.venv/bin/python run.py live --output "$${OUTPUT:-gemini-live.wav}" -- "$$AUDIO"

openai-asr:  ## OpenAI で ASR（文字起こし）（AUDIO）
	.venv/bin/python run_openai.py asr -- "$$AUDIO"

openai-tts:  ## OpenAI で TTS（読み上げ）（TEXT、OUTPUT）
	.venv/bin/python run_openai.py tts --output "$${OUTPUT:-openai-tts.wav}" -- "$$TEXT"

openai-dialogue:  ## OpenAI Realtime で設備を照会（24 kHz WAV の AUDIO、OUTPUT）
	.venv/bin/python run_openai.py dialogue --output "$${OUTPUT:-openai-dialogue.wav}" -- "$$AUDIO"

moshi-web:  ## GPU で LLM-jp-Moshi-v1 の Web UI を起動
	PATH="$(CURDIR)/.venv-moshi/bin:$$PATH" sh run_moshi_gpu.sh web

moshi-wav:  ## GPU で LLM-jp-Moshi-v1 に録音を入力（AUDIO、OUTPUT）
	PATH="$(CURDIR)/.venv-moshi/bin:$$PATH" sh run_moshi_gpu.sh wav "$$AUDIO" "$${OUTPUT:-moshi-reply.wav}"

moshi-wav-cpu:  ## 実験用の CPU 版 Moshi で録音を推論（AUDIO、OUTPUT）
	OMP_NUM_THREADS="$$THREADS" MKL_NUM_THREADS="$$THREADS" .venv-moshi-cpu/bin/python -m moshi.run_inference \
		--hf-repo llm-jp/llm-jp-moshi-v1 --device cpu --batch-size 1 -- "$$AUDIO" "$${OUTPUT:-moshi-cpu-reply.wav}"
