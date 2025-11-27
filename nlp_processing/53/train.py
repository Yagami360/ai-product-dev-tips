import argparse
import os

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments, default_data_collator

from trainer import LogitDistillationTrainer
from utils import print_gpu_memory, print_memory_summary, print_model_memory


def train(args):
    print("\n" + "=" * 60)
    print("Logit-based Knowledge Distillation")
    print("=" * 60)

    # トークナイザー（単語テキストをトークンIDに変換するモデル）
    # 教師の知識を正確に蒸留するために、教師モデルのトークナイザーを使用する
    print("\n📥 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        args.teacher_model_name,
        trust_remote_code=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "<|endoftext|>"})
    if tokenizer.eos_token is None:
        tokenizer.add_special_tokens({"eos_token": "<|im_end|>"})

    print(f"   Pad token: {tokenizer.pad_token} (ID: {tokenizer.pad_token_id})")
    print(f"   EOS token: {tokenizer.eos_token} (ID: {tokenizer.eos_token_id})")

    # 教師モデル（蒸留元モデル）
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
    if student_model.config.vocab_size != len(tokenizer):
        print(f"   ⚠️  Student-model vocab size mismatch! Resizing...")
        print(f"   Resizing student: {student_model.config.vocab_size} -> {len(tokenizer)}")
        student_model.resize_token_embeddings(len(tokenizer))

    # 教師モデルの語彙サイズをトークナイザーに合わせる
    # トークナイザーとして教師モデルのトークナイザーを使用しているので、通常は不要
    if teacher_model.config.vocab_size != len(tokenizer):
        print(f"   ⚠️  Teacher-model vocab size mismatch! Resizing...")
        print(f"   Resizing teacher: {teacher_model.config.vocab_size} -> {len(tokenizer)}")
        teacher_model.resize_token_embeddings(len(tokenizer))

    print("\n🔍 Validating vocab sizes after resizing...")
    print(f"   Tokenizer:  {len(tokenizer)}")
    print(f"   Teacher Model:    {teacher_model.config.vocab_size}")
    print(f"   Student Model:    {student_model.config.vocab_size}")

    # モデルの pad_token_id と eos_token_id をトークナイザーと一致させる
    teacher_model.config.pad_token_id = tokenizer.pad_token_id
    teacher_model.config.eos_token_id = tokenizer.eos_token_id
    student_model.config.pad_token_id = tokenizer.pad_token_id
    student_model.config.eos_token_id = tokenizer.eos_token_id

    # モデルのメモリ使用量の表示
    print_model_memory(teacher_model, f"Teacher Model: {args.teacher_model_name}")
    print_model_memory(student_model, f"Student Model: {args.student_model_name}")
    print_memory_summary(teacher_model, student_model, show_gpu=True)

    # データセット準備
    # GSM8K: 算数の問題と解答が含まれるデータセット
    print(f"\n📊 Loading dataset: GSM8K")
    dataset = load_dataset("gsm8k", "main", split="train[:]")
    print(f"✅ Dataset loaded: {len(dataset)} samples")

    # フォーマット変換: question と answer を結合して、入力テキストとして使用する
    # 入力データに answer の正解データが含まれることになるので、教師モデルに推論させる際に正解を教えていることになるのでは？という疑問が生じるが、
    # 蒸留における教師モデルの役割が、「正解を予測すること」ではなく、「正解を知っている状態での推論の『振る舞い』を提供すること」にあるので問題なし。
    dataset = dataset.map(lambda x: {"text": f"Q: {x['question']}\nA: {x['answer']}"})
    # dataset[0]: {
    #     'question': 'Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?',
    #     'answer': 'Natalia sold 48/2 = <<48/2=24>>24 clips in May.\nNatalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May.\n#### 72',
    #     'text': 'Q: Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?\nA: Natalia sold 48/2 = <<48/2=24>>24 clips in May.\nNatalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May.\n#### 72'
    # }
    print("[train] dataset[0]:", dataset[0])

    # データセットに含まれるテキストデータのトークン化: 単語テキストをトークナイザーで対応するトークンIDに変換する
    print("   Tokenizing dataset...")

    def tokenize_function(examples):
        # text の QA 部分だけ使用する
        tokenized = tokenizer(
            examples["text"],
            truncation=True,
            max_length=args.tokenizer_max_length,
            padding="max_length",
            return_tensors=None,
            add_special_tokens=True,
        )

        # labelsを追加
        # パディングトークンのラベルを -100 に設定して、損失計算から除外する
        # また、質問部分（"Q: ... A:" まで）も -100 に設定して、解答部分のみを学習対象にする
        labels = []
        for i, input_ids in enumerate(tokenized["input_ids"]):
            # 質問と解答の境界を見つける（"A:" の後のトークンから学習対象）
            # "A:" は通常 "\nA:" としてトークン化される
            text = examples["text"][i]
            question_answer_split = text.split("\nA:", 1)

            # 質問部分のトークン数を計算
            if len(question_answer_split) == 2:
                question_part = question_answer_split[0] + "\nA:"
                question_tokens = tokenizer(question_part, truncation=False, add_special_tokens=True)["input_ids"]
                question_length = len(question_tokens)
            else:
                question_length = 0

            # labels を作成：質問部分とパディング部分を -100 に設定
            label = []
            for j, token_id in enumerate(input_ids):
                if j < question_length:
                    # 質問部分は学習対象外（loss値の計算対象外）
                    label.append(-100)
                elif token_id == tokenizer.pad_token_id:
                    # パディング部分も学習対象外（loss値の計算対象外）
                    label.append(-100)
                else:
                    # 解答部分のみ学習対象
                    label.append(token_id)
            labels.append(label)
        tokenized["labels"] = labels
        return tokenized

    train_dataset = dataset.map(tokenize_function, batched=True, remove_columns=dataset.column_names)
    print(f"✅ Dataset ready: {len(train_dataset)} samples")

    # input_ids に `text` の部分のQAテキストが入っている
    # train_dataset[0]: {
    #     'input_ids': [48, 25, 41601, 685, 6088, 26111, 311, 220, 19, 23, 315, 1059, 4780, 304, 5813, 11, 323, 1221, 1340, 6088, 4279, 438, 1657, 26111, 304, 3217, 13, 2585, 1657, 26111, 1521, 41601, 685, 4559, 30055, 304, 5813, 323, 3217, 5267, 32, 25, 41601, 685, 6088, 220, 19, 23, 14, 17, 284, 1115, 19, 23, 14, 17, 28, 17, 19, 2452, 17, 19, 26111, 304, 3217, 624, 45, 4212, 685, 6088, 220, 19, 23, 10, 17, 19, 284, 1115, 19, 23, 10, 17, 19, 28, 22, 17, 2452, 22, 17, 26111, 30055, 304, 5813, 323, 3217, 624, 820, 220, 22, 17, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643, 151643],
    #     'attention_mask': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     'labels': [48, 25, 41601, 685, 6088, 26111, 311, 220, 19, 23, 315, 1059, 4780, 304, 5813, 11, 323, 1221, 1340, 6088, 4279, 438, 1657, 26111, 304, 3217, 13, 2585, 1657, 26111, 1521, 41601, 685, 4559, 30055, 304, 5813, 323, 3217, 5267, 32, 25, 41601, 685, 6088, 220, 19, 23, 14, 17, 284, 1115, 19, 23, 14, 17, 28, 17, 19, 2452, 17, 19, 26111, 304, 3217, 624, 45, 4212, 685, 6088, 220, 19, 23, 10, 17, 19, 284, 1115, 19, 23, 10, 17, 19, 28, 22, 17, 2452, 22, 17, 26111, 30055, 304, 5813, 323, 3217, 624, 820, 220, 22, 17, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100, -100]}
    print("train_dataset[0]:", train_dataset[0])

    # Training Arguments
    print("\n⚙️  Setting up training arguments...")
    training_args = TrainingArguments(
        output_dir=f"{args.output_dir}/{args.exper_name}",
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        logging_steps=args.logging_steps,
        logging_dir=f"{args.output_dir}/{args.exper_name}/logs",
        save_steps=args.save_steps,
        save_total_limit=args.save_total_limit,
        learning_rate=args.learning_rate,
        optim=args.optimizer,
        dataloader_pin_memory=True if torch.cuda.is_available() else False,
        remove_unused_columns=False,
        # fp16=True if torch.cuda.is_available() and not args.use_4bit else False,
    )

    # Trainer初期化
    print("\n🎓 Initializing LogitDistillationTrainer...")
    print(f"   Temperature: {args.distillation_logit_temperature}")
    print(f"   Alpha: {args.distillation_logit_alpha}")

    trainer = LogitDistillationTrainer(
        teacher_model=teacher_model,
        model=student_model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=default_data_collator,  # labels を上書きしないシンプルな collator
        temperature=args.distillation_logit_temperature,
        alpha=args.distillation_logit_alpha,
    )

    # 訓練開始
    print("\n🚀 Starting training...")
    print("=" * 60 + "\n")

    trainer.train()

    # モデル保存
    print("\n💾 Saving model...")
    trainer.save_model(f"{args.output_dir}/{args.exper_name}/checkpoint-final")
    tokenizer.save_pretrained(f"{args.output_dir}/{args.exper_name}/checkpoint-final")

    print("\n✅ Training complete!")
    print(f"   Model saved to: {args.output_dir}/{args.exper_name}/checkpoint-final")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Logit-based Knowledge Distillation")
    parser.add_argument("--exper_name", type=str, default="distill")
    parser.add_argument("--num_epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="The initial learning rate for AdamW.")
    parser.add_argument("--optimizer", type=str, default="adamw_torch", help="The optimizer to use.")
    parser.add_argument("--logging_steps", type=int, default=50)
    parser.add_argument("--save_steps", type=int, default=1000)
    parser.add_argument("--save_total_limit", type=int, default=4)
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--teacher_model_name", type=str, default="Qwen/Qwen2-7B-Instruct")
    parser.add_argument("--student_model_name", type=str, default="Qwen/Qwen2-0.5B-Instruct")
    parser.add_argument("--tokenizer_max_length", type=int, default=512)
    parser.add_argument("--distillation_logit_temperature", type=float, default=1.5)
    parser.add_argument("--distillation_logit_alpha", type=float, default=0.5)
    parser.add_argument("--use_4bit", action="store_true", default=False)
    args = parser.parse_args()

    print("=" * 60)
    print("実行条件")
    print("=" * 60)
    for key, value in vars(args).items():
        print(f"{key}: {value}")
    print("=" * 60)

    # 出力ディレクトリ作成
    os.makedirs(f"{args.output_dir}/{args.exper_name}", exist_ok=True)

    train(args)
