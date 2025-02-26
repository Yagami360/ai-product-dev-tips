import argparse
import os

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    # Trainer,
    # TrainingArguments
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, default=".results")
    args = parser.parse_args()

    print(args)

    # LLM モデルの定義
    model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen-14B-Chat-Int4",
        trust_remote_code=True
    ).eval()

    # tokenizer の定義
    tokenizer = AutoTokenizer.from_pretrained(
        "Qwen/Qwen-14B-Chat-Int4",
        trust_remote_code=True
    )
    # tokenizer.pad_token = (
    #     tokenizer.eos_token
    # )  # 終端文字 EOF トークンをパディングトークンとして設定
    # model.config.pad_token_id = (
    #     model.config.eos_token_id
    # )  # モデルのパディングトークンIDも設定

    # ファインチューニングした学習済みモデルで評価
    print("Evaluating model...")
    input_text = "今日は晴れです。散歩に行きましょう。"
    response, history = model.chat(
        tokenizer,
        input_text,
        history=None
        )
    print(response)
