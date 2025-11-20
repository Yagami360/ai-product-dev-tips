"""
GKD (Generalized Knowledge Distillation) を使用した知識蒸留の訓練スクリプト
https://huggingface.co/docs/trl/main/gkd_trainer

GKDの主な利点:
1. 訓練と推論の分布ミスマッチを解決
2. 生徒モデルが自己生成した出力に対して教師からフィードバックを受ける
3. 柔軟な損失関数の選択が可能
"""

import argparse
from pathlib import Path

from datasets import Dataset, load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GKDConfig, GKDTrainer


def prepare_dataset_for_gkd(dataset, tokenizer):
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
    """GKDを使用した知識蒸留の訓練"""

    print("=" * 60)
    print("GKD (Generalized Knowledge Distillation) Training")
    print("=" * 60)
    print(f"実験名: {args.exper_name}")
    print(f"教師モデル: {args.teacher_model_name}")
    print(f"生徒モデル: {args.student_model_name}")
    print(f"Lambda (生徒データ割合): {args.lmbda}")
    print(f"Beta (JSD補間係数): {args.beta}")
    print(f"Temperature: {args.temperature}")
    print(f"Sequence-Level KD: {args.seq_kd}")
    print("=" * 60)
    print()

    # 出力ディレクトリの設定
    output_dir = Path(args.output_dir) / args.exper_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # トークナイザーのロード
    print("📥 トークナイザーをロード中...")
    tokenizer = AutoTokenizer.from_pretrained(
        args.teacher_model_name, trust_remote_code=True
    )

    # パディングトークンの設定
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "<|pad|>"})

    # 量子化設定（4bit使用時）
    quantization_config = None
    if args.use_4bit:
        # BitsAndBytesConfigをインポートして使用
        import torch
        from transformers import BitsAndBytesConfig

        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

    # 教師モデルのロード
    print(f"📥 教師モデルをロード中: {args.teacher_model_name}")
    if args.use_4bit:
        teacher_model = AutoModelForCausalLM.from_pretrained(
            args.teacher_model_name,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True,
        )
    else:
        import torch

        teacher_model = AutoModelForCausalLM.from_pretrained(
            args.teacher_model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        )

    # 生徒モデルのロード
    print(f"📥 生徒モデルをロード中: {args.student_model_name}")
    # 生徒モデルは常にbf16で読み込む
    try:
        import torch

        student_model = AutoModelForCausalLM.from_pretrained(
            args.student_model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        )
    except ImportError:
        # torchがインポートできない場合は通常の読み込み
        student_model = AutoModelForCausalLM.from_pretrained(
            args.student_model_name,
            device_map="auto",
            trust_remote_code=True,
        )

    # 語彙サイズの調整（必要に応じて）
    if len(tokenizer) > student_model.config.vocab_size:
        print(
            f"⚠️  生徒モデルの語彙サイズを調整: {student_model.config.vocab_size} -> {len(tokenizer)}"
        )
        student_model.resize_token_embeddings(len(tokenizer))

    if len(tokenizer) > teacher_model.config.vocab_size:
        print(
            f"⚠️  教師モデルの語彙サイズを調整: {teacher_model.config.vocab_size} -> {len(tokenizer)}"
        )
        teacher_model.resize_token_embeddings(len(tokenizer))

    # メモリ使用量の表示（オプション）
    try:
        from utils import print_memory_summary

        print_memory_summary(teacher_model, student_model, show_gpu=True)
    except ImportError:
        # utilsがインポートできない場合はスキップ
        print("⚠️ メモリ使用量の表示をスキップ（utils.pyが見つかりません）")

    # データセットのロード
    print(f"\n📊 データセットをロード中: {args.dataset_name}")
    dataset = load_dataset(args.dataset_name, args.dataset_config, split="train")

    # データセットをGKD形式に変換
    train_dataset = prepare_dataset_for_gkd(dataset, tokenizer)

    # 評価用データセット（訓練データの一部を使用）
    eval_dataset = train_dataset.select(range(min(100, len(train_dataset))))

    print(f"✅ 訓練データ: {len(train_dataset)} samples")
    print(f"✅ 評価データ: {len(eval_dataset)} samples")

    # GKD設定
    training_args = GKDConfig(
        output_dir=str(output_dir),
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        save_total_limit=args.save_total_limit,
        evaluation_strategy="steps",
        eval_steps=args.save_steps,
        warmup_steps=100,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        gradient_checkpointing=True,
        fp16=False,
        bf16=True,
        optim=args.optimizer,
        # GKD特有のパラメータ
        temperature=args.temperature,
        lmbda=args.lmbda,  # 生徒データ割合（0.0-1.0）
        beta=args.beta,  # JSD補間係数（0.0=KL, 1.0=逆KL）
        max_new_tokens=args.max_new_tokens,
        seq_kd=args.seq_kd,  # Sequence-Level KD
        disable_dropout=True,
        report_to=["tensorboard"],
        logging_dir=str(output_dir / "logs"),
        push_to_hub=False,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
    )

    # GKDTrainerの初期化
    print("\n🎓 GKDTrainerを初期化中...")
    trainer = GKDTrainer(
        model=student_model,
        teacher_model=teacher_model,
        args=training_args,
        processing_class=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
    )

    # 訓練の実行
    print("\n🚀 訓練を開始します...")
    print("=" * 60)
    trainer.train()

    # モデルの保存
    print("\n💾 モデルを保存中...")
    trainer.save_model(str(output_dir / "checkpoint-final"))
    tokenizer.save_pretrained(str(output_dir / "checkpoint-final"))

    print(f"\n✅ 訓練が完了しました！")
    print(f"   モデルは以下に保存されました: {output_dir / 'checkpoint-final'}")
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
    parser.add_argument("--num_epochs", type=int, default=3, help="エポック数")
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
    parser.add_argument("--max_new_tokens", type=int, default=128, help="生成する最大トークン数")
    parser.add_argument("--seq_kd", action="store_true", help="Sequence-Level KDを使用")
    parser.add_argument(
        "--use_4bit", action="store_true", default=True, help="4bit量子化を使用"
    )

    args = parser.parse_args()
    train(args)
