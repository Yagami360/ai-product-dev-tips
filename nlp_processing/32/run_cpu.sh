#!/bin/sh
set -eux

docker run -it --rm -v $(pwd):/workspace \
    nvcr.io/nvidia/nemo:24.12 /bin/bash -c \
        "python3 run.py --device cpu"
