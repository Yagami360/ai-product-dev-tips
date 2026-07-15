# SensorLLM (Stage1) 推論/学習を GPU で動かすためのイメージ。
#
# ベースイメージの CUDA バージョン選定:
#   - torch 2.4.1 は cu121 ホイール（CUDA 12.1 ランタイムを内包）を使う。
#   - よって CUDA 12.1 系のベースを使う。ホストの NVIDIA ドライバ(例: 560 / CUDA 12.6)は
#     CUDA 12.1 に後方互換なので問題ない（実行時は --gpus all で host ドライバを利用）。
#   - torch は CUDA/cuDNN を内包するため、軽い -runtime タグで十分（-devel は不要）。
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    UV_LINK_MODE=copy \
    HF_HUB_ENABLE_HF_TRANSFER=0 \
    # venv を /app の外に作る（実行時に -v $(PWD):/app でマウントしても隠れないように）
    UV_PROJECT_ENVIRONMENT=/opt/uv-venv \
    # 焼き込んだ SensorLLM を import できるようにする
    PYTHONPATH=/opt/SensorLLM

RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# uv を導入（Python は uv が pyproject の requires-python に従って自動取得する）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 公式リポジトリを clone（再現性のためコミット固定）。
# 非公式 ckpt(1EE1) は chronos-t5-base(d_model=768) で学習されているため、
# ts_backbone.yaml の既定(chronos-t5-large/1024)を base/768 に調整して焼き込む。
ARG SENSORLLM_REF=ddd17fecb508fcfa5ae156dbd37902e3ddbf652a
RUN git clone https://github.com/cruiseresearchgroup/SensorLLM /opt/SensorLLM \
    && git -C /opt/SensorLLM checkout ${SENSORLLM_REF} \
    && sed -i 's/name: "chronos-t5-large"/name: "chronos-t5-base"/; s/encoder_output_dim: 1024/encoder_output_dim: 768/' \
        /opt/SensorLLM/sensorllm/model/ts_backbone.yaml

# train.py は `evaluate.load("../metrics/<name>")` を cwd=/opt/SensorLLM から参照する。
# = /opt/metrics/<name>/<name>.py。学習時のみ必要なローカルメトリクスを焼き込む。
RUN for m in f1 accuracy precision recall; do \
        mkdir -p /opt/metrics/$m; \
        curl -fsSL -o /opt/metrics/$m/$m.py \
          https://raw.githubusercontent.com/huggingface/evaluate/main/metrics/$m/$m.py; \
    done

WORKDIR /app

# 依存定義だけをコピーして uv sync（依存レイヤをキャッシュ／venv は UV_PROJECT_ENVIRONMENT に作られる）。
# 推論に加え学習/データ生成も回せるよう train extra も同梱する。
# predict.py / モデル / .env は実行時にカレントを /app へマウントして渡す（COPY しない）。
COPY pyproject.toml ./
RUN uv sync --extra cu121 --extra train

CMD ["bash"]
