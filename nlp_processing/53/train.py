import argparse
import os

from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, DataCollatorForLanguageModeling, TrainingArguments

from trainer import LogitDistillationTrainer
from utils import print_model_memory, print_gpu_memory, print_memory_summary


def train(args):
    print("\n" + "=" * 60)
    print("Logit-based Knowledge Distillation")
    print("=" * 60)

    # トークナイザーの読み込み
    print("\n📥 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.teacher_model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    # 教師モデル（蒸留元モデル）
    print(f"📥 Loading teacher model: {args.teacher_model_name}")
    teacher_model = AutoModelForCausalLM.from_pretrained(
        args.teacher_model_name,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype="auto",  # 自動でdtype選択
        # load_in_4bit=True  # bitsandbytes が必要（Mac では動作しない）
    )

    # 生徒モデル（蒸留先モデル）
    print(f"📥 Loading student model: {args.student_model_name}")
    student_model = AutoModelForCausalLM.from_pretrained(args.student_model_name, torch_dtype="auto")
    print(f"   Resizing student embeddings: {student_model.config.vocab_size} -> {len(tokenizer)}")
    student_model.resize_token_embeddings(len(tokenizer))

    # モデルのメモリ使用量の表示
    print_model_memory(teacher_model, "Teacher Model")
    print_model_memory(student_model, "Student Model")
    print_memory_summary(teacher_model, student_model, show_gpu=True)

    # データセット準備
    print(f"\n📊 Loading dataset: GSM8K (train[:1000])")
    dataset = load_dataset("gsm8k", "main", split="train[:1000]")

    # フォーマット変換
    dataset = dataset.map(lambda x: {"text": f"Q: {x['question']}\nA: {x['answer']}"})

    # トークン化
    print("   Tokenizing dataset...")
    train_dataset = dataset.map(
        lambda x: tokenizer(x["text"], truncation=True, max_length=256, padding="max_length"), batched=True, remove_columns=dataset.column_names
    )
    print(f"✅ Dataset ready: {len(train_dataset)} samples")

    # Training Arguments
    print("\n⚙️  Setting up training arguments...")
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        # CPU/MPS最適化
        fp16=False,  # MacではFalse
        # fp16=True,  # GPU(CUDA)の場合はTrue
        # ログ設定
        logging_steps=10,
        logging_dir=f"{args.output_dir}/logs",
        # 保存設定
        save_steps=100,
        save_total_limit=2,
        # その他
        report_to="none",  # wandb等を無効化
        dataloader_pin_memory=False,  # MacではFalse推奨
        remove_unused_columns=False,
    )

    # Trainer初期化
    print("\n🎓 Initializing LogitDistillationTrainer...")
    print(f"   Temperature: {args.distillation_logit_temperature}")
    print(f"   Alpha: {args.distillation_logit_alpha}")

    trainer = LogitDistillationTrainer(
        teacher_model=teacher_model,
        model=student_model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
        temperature=args.distillation_logit_temperature,
        alpha=args.distillation_logit_alpha,
    )

    # 訓練開始
    print("\n🚀 Starting training...")
    print("=" * 60 + "\n")

    trainer.train()

    # モデル保存
    print("\n💾 Saving model...")
    trainer.save_model(f"{args.output_dir}/final_model")
    tokenizer.save_pretrained(f"{args.output_dir}/final_model")

    print("\n✅ Training complete!")
    print(f"   Model saved to: {args.output_dir}/final_model")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logit-based Knowledge Distillation")
    parser.add_argument("--num_epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--teacher_model_name", type=str, default="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
    parser.add_argument("--student_model_name", type=str, default="distilgpt2")
    parser.add_argument("--distillation_logit_temperature", type=float, default=2.0)
    parser.add_argument("--distillation_logit_alpha", type=float, default=0.5)
    args = parser.parse_args()

    print("=" * 60)
    print("実行条件")
    print("=" * 60)
    for key, value in vars(args).items():
        print(f"{key}: {value}")
    print("=" * 60)

    # 出力ディレクトリ作成
    os.makedirs(args.output_dir, exist_ok=True)

    train(args)
