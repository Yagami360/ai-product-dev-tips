# コード雛形 リファレンス（コード付き Tip）

Tip が必要とするファイルだけを生成する。
常に近くの兄弟 Tip のファイルから始めて調整すること。
バージョン・ベースイメージ・依存の固定は、そのカテゴリで既に使われているものに合わせる。
以下のテンプレートはリポジトリの慣習を捉えたもの。

## Python エントリポイント（`train.py` / `predict.py` / `run.py`）

- `argparse` で引数を解析する。
  多くは `--device {cpu,cuda}` の選択肢を持つ。
- 実ロジックは `if __name__ == "__main__":` の下に書く。
- 教材的な例なので、最小限で読みやすく保つ。

```python
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=str, default="cuda", choices=["cpu", "cuda"])
    args = parser.parse_args()

    # ... Tip の中心的なロジック ...
```

## `requirements.txt`

バージョン固定の依存。
最も近い既存 Tip のスタイル（`~=`, `>=`, `==` の混在）を流用する。
Dockerfile がすでにインストールするものの上に、Tip が必要とするものだけを列挙する。

## `Dockerfile`

リポジトリ全体で使われている CUDA/Ubuntu テンプレート（`nlp_processing/29/Dockerfile` 参照）を調整する。
主な要素は次の通り。

```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt upgrade -y && \
    apt install -y wget curl && \
    apt install --no-install-recommends -y git make build-essential ... jq

ARG WORKDIR="/app"
ENV WORKDIR=${WORKDIR}

RUN apt install --no-install-recommends -y python3 python3-pip python3-setuptools
RUN pip3 install --upgrade pip

# フレームワーク固有のライブラリをここでインストール（torch / transformers / 等）

WORKDIR ${WORKDIR}
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . ${WORKDIR}
WORKDIR ${WORKDIR}

RUN apt purge -y build-essential
RUN ldconfig && apt-get -y clean && apt-get -y autoremove && rm -rf /var/lib/apt/lists/* /tmp/*
```

ベンダーイメージ（例: NeMo）の上に作る Tip では、`Dockerfile` は不要なことがある。
その場合は実行スクリプトが上流イメージを直接 `docker run` すればよい（`nlp_processing/32` 参照）。
また画像処理系のように Docker を使わず、ローカルの Python で完結する軽量な Tip では Dockerfile を作らない（`image_processing/11` 参照）。

## 実行スクリプト `*_cpu.sh` / `*_gpu.sh`

`#!/bin/sh` + `set -eux` で始める。
イメージが無ければビルドし、その後エントリポイントを `docker run` する。
`_gpu` 版は `--gpus all` を足す。
`nlp_processing/29/train_gpu.sh` のパターンは次の通り。

```sh
#!/bin/sh
set -eux

WORKDIR=${WORKDIR:-"/app"}
IMAGE_NAME=${IMAGE_NAME:-"<image-name>"}
TAG=${TAG:-"latest"}
PROJECT_DIR=${PWD}

# ハイパーパラメータ / 引数をシェル変数として
EPOCHS=5

if ! docker images ${IMAGE_NAME}:${TAG} | grep -q ${IMAGE_NAME}; then
    docker build -t ${IMAGE_NAME}:${TAG} -f Dockerfile .
fi

docker run --rm --gpus all -v ${PROJECT_DIR}:${WORKDIR} \
    ${IMAGE_NAME}:${TAG} /bin/bash -c "python3 train.py --epochs ${EPOCHS}"
```

最もシンプルな形（ベンダーイメージ、ビルドなし）は `nlp_processing/32/run_gpu.sh` の通り。

```sh
#!/bin/sh
set -eux

docker run --gpus all -it --rm -v $(pwd):/workspace \
    nvcr.io/nvidia/nemo:24.12 /bin/bash -c "python3 run.py --device cuda"
```

Docker を使わない画像処理系の軽量スクリプトは、`image_processing/11` のように、入力ディレクトリを引数で渡して Python を直接呼ぶ形が多い。
`_cpu.sh` 版は `--gpus all` を外し、`--device cpu` を渡す。
