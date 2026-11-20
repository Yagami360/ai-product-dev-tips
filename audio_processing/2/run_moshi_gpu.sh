#!/bin/sh
set -eu

model=llm-jp/llm-jp-moshi-v1

case "${1:-}" in
    web)
        if [ "$#" -eq 1 ]; then
            exec python -m moshi.server --hf-repo "$model" --device cuda --port 8998
        fi
        ;;
    wav)
        if [ "$#" -eq 3 ]; then
            exec python -m moshi.run_inference --hf-repo "$model" --device cuda \
                --batch-size 1 -- "$2" "$3"
        fi
        ;;
esac

printf 'Usage: sh run_moshi_gpu.sh web | wav INPUT.wav OUTPUT.wav\n' >&2
exit 2
