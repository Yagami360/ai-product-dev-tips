"""AI Scientist-v2 の LLM バックエンド疎通チェック（配線 smoke test）。

選んだモデル文字列（プレフィックス方式）が、AI Scientist-v2 本体の LLM レイヤ
（ai_scientist.llm）経由で正しくバックエンドにルーティングされ、応答を返すかを確認する。
ideation / experiment を回す前の「まず繋がるか」を数秒で確かめる用途。

使い方:
    1. AI-Scientist-v2 を clone し、conda 環境で `pip install -r requirements.txt` 済みにする。
    2. このファイルを AI-Scientist-v2 リポジトリ直下にコピーする（`ai_scientist` を import するため）。
    3. モデルに応じて API キー等を設定して実行する:
         # ローカル LLM（Qwen など）: ollama serve を起動しモデルを pull 済みにする
         export OLLAMA_API_KEY=ollama
         python check_wiring.py --model ollama/qwen3:8b
         # Gemini
         export GEMINI_API_KEY=...
         python check_wiring.py --model gemini-2.5-pro
         # Claude
         export ANTHROPIC_API_KEY=...
         python check_wiring.py --model claude-3-5-sonnet-20241022

注意: create_client / get_response_from_llm は AVAILABLE_LLMS のメンバーシップを（argparse と違い）
チェックしないため、AVAILABLE_LLMS に未登録のモデル文字列（例: 現行の gemini-3.1-pro-preview）でも
このスクリプトからは疎通確認できる。ideation/launch の CLI で使う場合は llm.py の AVAILABLE_LLMS に
1 行追記が必要。
"""

import argparse

from ai_scientist.llm import create_client, get_response_from_llm


def main():
    parser = argparse.ArgumentParser(
        description="AI Scientist-v2 の LLM バックエンド疎通チェック"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="ollama/qwen3:8b",
        help="モデル文字列（例: ollama/qwen3:8b, gemini-2.5-pro, claude-3-5-sonnet-20241022）",
    )
    args = parser.parse_args()

    client, model = create_client(args.model)
    text, _ = get_response_from_llm(
        prompt="Reply with exactly one word: WIRING_OK.",
        client=client,
        model=model,
        system_message="You are a terse assistant.",
        temperature=0.0,
    )
    print(f"model={model!r} -> response={text.strip()!r}")
    if "WIRING_OK" in text:
        print("[OK] LLM バックエンド疎通成功")
    else:
        print("[WARN] 応答は得られたが WIRING_OK を含まない（モデル依存の可能性）")


if __name__ == "__main__":
    main()
