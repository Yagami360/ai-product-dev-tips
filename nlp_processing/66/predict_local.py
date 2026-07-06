import argparse
import os

from openai import OpenAI


# =============================================================================
# 【パターン B】CPU でも動く軽量な量子化版 MiniMax-M3（GGUF）を、
#              llama.cpp の OpenAI 互換サーバー（llama-server）経由で叩くサンプル。
#   - run_llama_cpp_cpu.sh で llama-server を起動しておく（既定 http://localhost:8080/v1）。
#   - api_key はダミー（llama-server は既定で認証不要。"EMPTY" 等を渡す）。
#   - model 文字列は llama-server 側で無視される（起動時にロードした GGUF が使われる）。
#   - サンプリングは Unsloth 推奨の temp=1.0 / top_p=0.95 / top_k=40（top_k は extra_body で渡す）。
#   注意:
#   - この GGUF 版は llama.cpp が MiniMax Sparse Attention (MSA) 未対応のため dense attention に
#     フォールバックする（＝長文脈の効率化は効かない）。CPU での「まず動かす」検証用。
#   - reasoning（thinking）の細かな切替は公式 API 版（predict_api.py）とは仕組みが異なるため、
#     このローカル版では送らない（モデル既定の思考挙動になる）。
# =============================================================================


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, default="MiniMax-M3 の MiniMax Sparse Attention (MSA) の要点を 3 行で説明して。")
    # llama-server はロード済みモデルを使うため、この値は表示上のラベル程度の意味しか持たない
    parser.add_argument("--model", type=str, default="minimax-m3")
    parser.add_argument("--base-url", type=str, default="http://localhost:8080/v1")
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--top-k", type=int, default=40)
    parser.add_argument("--stream", action="store_true", help="ストリーミング出力にする")
    parser.add_argument("--max-tokens", type=int, default=1024)
    args = parser.parse_args()

    # llama-server は既定で認証不要。ダミーキーを渡す（環境変数があればそれを使う）
    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")

    client = OpenAI(api_key=api_key, base_url=args.base_url)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": args.prompt},
    ]

    # top_k は OpenAI SDK の標準引数に無いため extra_body で渡す
    extra_body = {"top_k": args.top_k}

    if args.stream:
        stream = client.chat.completions.create(
            model=args.model, messages=messages, max_tokens=args.max_tokens,
            temperature=args.temperature, top_p=args.top_p, stream=True, extra_body=extra_body,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                print(delta.content, end="", flush=True)
        print()
    else:
        resp = client.chat.completions.create(
            model=args.model, messages=messages, max_tokens=args.max_tokens,
            temperature=args.temperature, top_p=args.top_p, extra_body=extra_body,
        )
        print(resp.choices[0].message.content)
