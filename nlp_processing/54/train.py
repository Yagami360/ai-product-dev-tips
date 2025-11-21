import argparse
import os
from pathlib import Path

import torch
from datasets import Dataset, load_dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer,
                          BitsAndBytesConfig)
from trl import GKDConfig, GKDTrainer

from utils import print_gpu_memory, print_memory_summary, print_model_memory


def prepare_dataset(dataset, tokenizer):
    """
    GKDTrainer用にデータセットを準備
    GKDTrainerは "messages" 形式のデータを期待する
    """
    messages_data = []

    for example in dataset:
        messages = [
            {"role": "user", "content": f"Q: {example['question']}"},
            {"role": "assistant", "content": f"A: {example['answer']}"},
        ]
        messages_data.append(messages)

    return Dataset.from_dict({"messages": messages_data})


def train(args):
    # トークナイザー（単語テキストをトークンIDに変換するモデル）
    # 教師の知識を正確に蒸留するために、教師モデルのトークナイザーを使用する
    print("\n📥 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        args.teacher_model_name,
        trust_remote_code=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "<|pad|>"})
    if tokenizer.eos_token is None:
        tokenizer.add_special_tokens({"pad_token": "<|endoftext|>"})

    print(f"   Pad token: {tokenizer.pad_token} (ID: {tokenizer.pad_token_id})")
    print(f"   EOS token: {tokenizer.eos_token} (ID: {tokenizer.eos_token_id})")

    # 教師モデルのロード
    print(f"📥 Loading teacher model: {args.teacher_model_name}")
    if args.use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            # bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        teacher_model = AutoModelForCausalLM.from_pretrained(
            args.teacher_model_name,
            trust_remote_code=True,
            device_map="auto",
            torch_dtype="auto",
            # torch_dtype=torch.float16,
            quantization_config=bnb_config,
        )
    else:
        teacher_model = AutoModelForCausalLM.from_pretrained(
            args.teacher_model_name,
            trust_remote_code=True,
            device_map="auto",
            torch_dtype="auto",
            # torch_dtype=torch.float16,
        )

    # 生徒モデル（蒸留先モデル）
    print(f"📥 Loading student model: {args.student_model_name}")
    student_model = AutoModelForCausalLM.from_pretrained(
        args.student_model_name,
        trust_remote_code=True,
        device_map="auto",
        torch_dtype="auto",
        # torch_dtype=torch.float16,
        # 生徒モデルは、4bit 量子化利用不可
        # load_in_4bit=True if args.use_4bit else False,
    )

    # 生徒モデルの語彙サイズを教師モデル（のトークナイザー）に合わせる
    # 蒸留時には、教師モデルのトークナイザーのみを使用するためにアンマッチが生じるため必要
    # 語彙サイズ（Vocabulary Size）: モデルが扱えるトークン（単語の最小単位）の種類の数
    if len(tokenizer) != student_model.config.vocab_size:
        print(
            f"⚠️  生徒モデルの語彙サイズを調整: {student_model.config.vocab_size} -> {len(tokenizer)}"
        )
        student_model.resize_token_embeddings(len(tokenizer))

    # 教師モデルの語彙サイズをトークナイザーに合わせる
    # トークナイザーとして教師モデルのトークナイザーを使用しているので、通常は不要
    if len(tokenizer) != teacher_model.config.vocab_size:
        print(
            f"⚠️  教師モデルの語彙サイズを調整: {teacher_model.config.vocab_size} -> {len(tokenizer)}"
        )
        teacher_model.resize_token_embeddings(len(tokenizer))

    # モデルの pad_token_id と eos_token_id をトークナイザーと一致させる
    teacher_model.config.pad_token_id = tokenizer.pad_token_id
    teacher_model.config.eos_token_id = tokenizer.eos_token_id
    student_model.config.pad_token_id = tokenizer.pad_token_id
    student_model.config.eos_token_id = tokenizer.eos_token_id

    # モデルのメモリ使用量の表示
    print_model_memory(teacher_model, f"Teacher Model: {args.teacher_model_name}")
    print_model_memory(student_model, f"Student Model: {args.student_model_name}")
    print_memory_summary(teacher_model, student_model, show_gpu=True)

    # データセットのロード
    print(f"\n📊 データセットをロード中: {args.dataset_name}")
    dataset = load_dataset(args.dataset_name, args.dataset_config, split="train")
    train_dataset = prepare_dataset(dataset, tokenizer)
    eval_dataset = train_dataset.select(range(min(100, len(train_dataset))))
    print(f"✅ 訓練データ: {len(train_dataset)} samples")
    print(f"✅ 評価データ: {len(eval_dataset)} samples")

    # GKDTrainer の設定
    training_args = GKDConfig(
        output_dir=f"{args.output_dir}/{args.exper_name}",
        logging_dir=f"{args.output_dir}/{args.exper_name}/logs",
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        save_total_limit=args.save_total_limit,
        eval_strategy="steps",
        eval_steps=args.save_steps,
        warmup_steps=100,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        gradient_checkpointing=True,
        # fp16=True if torch.cuda.is_available() and not args.use_4bit else False,
        # bf16=True if torch.cuda.is_available() and args.use_4bit else False,
        optim=args.optimizer,
        temperature=args.temperature,
        lmbda=args.lmbda,       # 生徒データ割合（0.0-1.0）
        beta=args.beta,         # JSD補間係数（0.0=KL, 1.0=逆KL）
        max_new_tokens=args.max_new_tokens,
        seq_kd=args.seq_kd,     # Sequence-Level KD
        disable_dropout=True,
        report_to=["tensorboard"],
        push_to_hub=False,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
    )
    trainer = GKDTrainer(
        model=student_model,
        teacher_model=teacher_model,
        args=training_args,
        processing_class=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )

    # 学習の実行
    print("\n🚀 学習を開始します...")
    print("=" * 60)
    trainer.train()

    # モデルの保存
    print("\n💾 モデルを保存中...")
    trainer.save_model(f"{args.output_dir}/{args.exper_name}/checkpoint-final")
    tokenizer.save_pretrained(f"{args.output_dir}/{args.exper_name}/checkpoint-final")
    print(f"\n✅ 訓練が完了しました！")
    print(f"   モデルは以下に保存されました: {args.output_dir}/{args.exper_name}/checkpoint-final")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GKDを使用した知識蒸留")
    parser.add_argument("--exper_name", type=str, required=True, help="実験名")
    parser.add_argument("--output_dir", type=str, default="outputs", help="出力ディレクトリ")
    parser.add_argument("--teacher_model_name", type=str, required=True, help="教師モデル名")
    parser.add_argument("--student_model_name", type=str, required=True, help="生徒モデル名")
    parser.add_argument(
        "--dataset_name", type=str, default="openai/gsm8k", help="データセット名"
    )
    parser.add_argument("--dataset_config", type=str, default="main", help="データセット設定")
    parser.add_argument("--num_epochs", type=int, default=5, help="エポック数")
    parser.add_argument("--batch_size", type=int, default=2, help="バッチサイズ")
    parser.add_argument(
        "--gradient_accumulation_steps", type=int, default=4, help="勾配累積ステップ数"
    )
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="学習率")
    parser.add_argument("--optimizer", type=str, default="adamw_torch", help="オプティマイザ")
    parser.add_argument("--logging_steps", type=int, default=50, help="ログ出力間隔")
    parser.add_argument("--save_steps", type=int, default=500, help="保存間隔")
    parser.add_argument(
        "--save_total_limit", type=int, default=3, help="保存するチェックポイント数の上限"
    )
    parser.add_argument("--temperature", type=float, default=0.9, help="サンプリング温度")
    parser.add_argument("--lmbda", type=float, default=0.7, help="生徒データ割合 (0.0-1.0)")
    parser.add_argument(
        "--beta", type=float, default=0.5, help="JSD補間係数 (0.0=KL, 1.0=逆KL)"
    )
    parser.add_argument("--max_new_tokens", type=int, default=512, help="生成する最大トークン数")
    parser.add_argument("--seq_kd", action="store_true", help="Sequence-Level KDを使用")
    parser.add_argument(
        "--use_4bit", action="store_true", default=False, help="4bit量子化を使用"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("実行条件")
    print("=" * 60)
    for key, value in vars(args).items():
        print(f"{key}: {value}")
    print("=" * 60)

    os.makedirs(f"{args.output_dir}/{args.exper_name}", exist_ok=True)
    train(args)
