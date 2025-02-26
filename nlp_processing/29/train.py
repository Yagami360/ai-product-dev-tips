import argparse
import os

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments
)

from datasets import load_dataset


def tokenize_function(examples):
    outputs = tokenizer(
        examples["text"],
        truncation=True,
        max_length=512,
        padding="max_length",
        return_tensors="pt",
    )

    # GPT-2の学習では、入力シーケンスを1つずらしたものをラベルとして使用する必要がある
    outputs["labels"] = outputs["input_ids"].clone()
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name",
        type=str,
        choices=[
            # GPT-2 系
            # OpenAI の GPT3.5, GPT-4 などの商用モデルに関しては、この方法ではファインチューニングができない。
            # GPT3.5, GPT-4 をファインチューニングしたい場合は、OpenAI API を使用して、OpenAI サーバー側で行うことができるようになっている
            "gpt2", "gpt2-medium", "gpt2-large", "gpt2-xl",
            # Qwen 系
            "Qwen/Qwen-7B", "Qwen/Qwen-14B"
        ],
        default="gpt2",
    )
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--learning_rate", type=float, default=2e-5)
    parser.add_argument("--save_steps", type=int, default=1000)
    parser.add_argument("--output_dir", type=str, default=".results")
    args = parser.parse_args()

    print(args)

    # LLM モデルの定義
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        device_map="auto"        # デバイスの自動割り当て
    )

    # tokenizer の定義
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        padding_side="right"
    )
    # if args.model_name in ["gpt2", "gpt2-medium", "gpt2-large", "gpt2-xl"]:
    # 終端文字 EOF トークンをパディングトークンとして設定
    tokenizer.pad_token = (
        tokenizer.eos_token
    )
    # モデルのパディングトークンIDも設定
    model.config.pad_token_id = (
        model.config.eos_token_id
    )

    # データセットの読み込み
    print("Loading dataset...")
    dataset = load_dataset("tiny_shakespeare", cache_dir="/datasets/tiny_shakespeare", trust_remote_code=True)
    # dataset = load_dataset("graelo/wikipedia", "20230901.ja", cache_dir="/datasets/wikipedia", trust_remote_code=True)
    print("\ndataset:\n", dataset)
    print(dataset["train"][0]["text"][:200])

    # データセットの保存
    # output_file = f"/datasets/{dataset_name}.txt"
    # os.makedirs(os.path.dirname(output_file), exist_ok=True)
    # with open(output_file, "w", encoding="utf-8") as f:
    #     for item in dataset["train"]:
    #         f.write(item["text"] + "\n\n")

    # データセットのトークン化
    tokenized_dataset = dataset.map(
        tokenize_function, batched=True, remove_columns=dataset["train"].column_names
    )

    # 学習（ファインチューニング）の設定
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        save_steps=args.save_steps,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
    )

    # 学習（ファインチューニング）開始
    print("Start training...")
    trainer.train()
    print("Training completed.")

    # ファインチューニングした学習済みモデルの保存
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("Model saved to", args.output_dir)

    # ファインチューニングした学習済みモデルの読み込み
    model = AutoModelForCausalLM.from_pretrained(args.output_dir)
    tokenizer = AutoTokenizer.from_pretrained(args.output_dir)
    print("Model loaded from", args.output_dir)

    # ファインチューニングした学習済みモデルで評価
    print("Evaluating model...")
    input_text = "今日は晴れです。散歩に行きましょう。"
    inputs = tokenizer(input_text, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=512)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(generated_text)
