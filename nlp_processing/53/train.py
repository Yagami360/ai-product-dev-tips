import argparse
import os

from datasets import Dataset, load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, DataCollatorForLanguageModeling, TrainingArguments

from trainer import LogitDistillationTrainer


def train(args):
    # トークナイザーの読み込み
    tokenizer = AutoTokenizer.from_pretrained(args.teacher_model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    # 教師モデル（蒸留元モデル）
    teacher_model = AutoModelForCausalLM.from_pretrained(
        args.teacher_model_name,
        device_map="auto",
        trust_remote_code=True,
        # load_in_4bit=True     # bitsandbytes のインストールが必要（Mac では動作しない）
    )

    # 生徒モデル（蒸留先モデル）
    student_model = AutoModelForCausalLM.from_pretrained(args.student_model_name)
    student_model.resize_token_embeddings(len(tokenizer))

    # Data
    dataset = load_dataset("gsm8k", "main", split="train[:1000]")
    dataset = dataset.map(lambda x: {"text": f"Q: {x['question']}\nA: {x['answer']}"})
    train_dataset = dataset.map(
        lambda x: tokenizer(x["text"], truncation=True, max_length=256, padding="max_length"), batched=True, remove_columns=dataset.column_names
    )

    # Training
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        fp16=True,
    )

    trainer = LogitDistillationTrainer(
        teacher_model=teacher_model,
        model=student_model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
        temperature=args.distillation_logit_temperature,
        alpha=args.distillation_logit_alpha,
    )

    trainer.train()


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--num_epochs", type=int, default=10)
    args.add_argument("--batch_size", type=int, default=8)
    args.add_argument("--output_dir", type=str, default="outputs")
    args.add_argument("--teacher_model_name", type=str, default="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")
    args.add_argument("--student_model_name", type=str, default="distilgpt2")
    args.add_argument("--distillation_logit_temperature", type=float, default=2.0)
    args.add_argument("--distillation_logit_alpha", type=float, default=0.5)
    args = args.parse_args()

    print("----------------------------------------------")
    print("実行条件")
    print("----------------------------------------------")
    for key, value in vars(args).items():
        print(f"{key}: {value}")

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)

    train(args)
