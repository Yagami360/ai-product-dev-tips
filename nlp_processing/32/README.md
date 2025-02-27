# NVIDIA NeMo を使用して LLM の推論処理を行う

## 使用方法

1. GPU ありのインスタンス環境を用意する

1. NVIDIA NeMo をインストールする

    - pip を使用する場合
        ```bash
        apt-get update && apt-get install -y libsndfile1 ffmpeg
        pip install Cython packaging
        pip install nemo_toolkit['all']
        ```

    - （推奨）Docker を使用する場合
        ```bash
        docker pull nvcr.io/nvidia/nemo:24.12
        ```

1. NeMo を使用したスクリプトを作成する

    - 例: [`run.py`](run.py)

1. NeMo を使用したスクリプトを実行する

    - Docker を使用する場合
        ```bash
        docker run --gpus all -it --rm -v $(pwd):/workspace \
            nvcr.io/nvidia/nemo:24.12 /bin/bash -c \
                "python3 run.py --device cuda"
        ```

## 参考サイト

- 公式ユーザーガイド: https://docs.nvidia.com/nemo-framework/user-guide/latest/overview.html
