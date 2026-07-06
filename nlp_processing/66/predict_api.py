import argparse
import base64
import os
import mimetypes

from openai import OpenAI


# =============================================================================
# 【パターン A】MiniMax-M3 を MiniMax 公式クラウド API（OpenAI 互換）経由で叩く最小サンプル。
#   - base_url を https://api.minimax.io/v1 にするだけで OpenAI SDK がそのまま使える。
#   - モデル ID は "MiniMax-M3" 固定。ローカル GPU 不要。
#   - reasoning（思考）は extra_body の "thinking" で adaptive / disabled / enabled を切り替える
#     （公式 API 専用の指定。ローカル自ホスト版は predict_local.py を参照）。
#   - 画像を渡すとネイティブ・マルチモーダル（image-text-to-text）として応答する。
# =============================================================================


def encode_image_data_uri(image_path):
    """ローカル画像を data URI（base64）に変換する。OpenAI 互換の image_url に載せる。"""
    mime, _ = mimetypes.guess_type(image_path)
    mime = mime or "image/jpeg"
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def build_messages(prompt, image_path):
    """テキストのみ / 画像＋テキスト の messages を組み立てる。"""
    if image_path is None:
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": encode_image_data_uri(image_path)}},
            ],
        },
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, default="MiniMax-M3 の MiniMax Sparse Attention (MSA) の要点を 3 行で説明して。")
    parser.add_argument("--model", type=str, default="MiniMax-M3")
    parser.add_argument("--base-url", type=str, default="https://api.minimax.io/v1")
    parser.add_argument("--thinking", type=str, default="adaptive", choices=["adaptive", "disabled", "enabled"],
                        help="reasoning モード。adaptive=必要時のみ思考 / disabled=思考せず即答 / enabled=常に思考")
    parser.add_argument("--image", type=str, default=None, help="画像パス（指定するとマルチモーダル入力になる）")
    parser.add_argument("--stream", action="store_true", help="ストリーミング出力にする")
    parser.add_argument("--max-tokens", type=int, default=1024)
    args = parser.parse_args()

    # API キーは環境変数 MINIMAX_API_KEY（無ければ OPENAI_API_KEY）から読む
    api_key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("環境変数 MINIMAX_API_KEY に MiniMax の API キーを設定してください。")

    client = OpenAI(api_key=api_key, base_url=args.base_url)

    messages = build_messages(args.prompt, args.image)

    # thinking は OpenAI SDK の標準引数に無いため extra_body で渡す（{"type": "..."} のオブジェクト形式）
    extra_body = {"thinking": {"type": args.thinking}}

    if args.stream:
        stream = client.chat.completions.create(
            model=args.model, messages=messages, max_tokens=args.max_tokens, stream=True, extra_body=extra_body,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                print(delta.content, end="", flush=True)
        print()
    else:
        resp = client.chat.completions.create(
            model=args.model, messages=messages, max_tokens=args.max_tokens, extra_body=extra_body,
        )
        print(resp.choices[0].message.content)
