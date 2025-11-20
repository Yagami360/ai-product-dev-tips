"""
GKDで訓練したモデルの推論スクリプト
"""

import argparse
import json
from pathlib import Path

from datasets import load_dataset
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer


def predict(args):
    """モデルの推論と評価"""

    print("=" * 60)
    print("Model Inference and Evaluation")
    print("=" * 60)
    print(f"Model: {args.model_name}")
    print(f"Dataset: {args.dataset_name}")
    print(f"Num samples: {args.num_samples}")
    print(f"Batch size: {args.batch_size}")
    print("=" * 60)
    print()

    # モデル名から出力ディレクトリを決定
    if "/" in args.model_name:
        # Hugging Faceモデルの場合
        model_basename = args.model_name.replace("/", "_")
    else:
        # ローカルモデルの場合
        model_basename = Path(args.model_name).name

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # トークナイザーのロード
    print("📥 トークナイザーをロード中...")
    if "checkpoint" in args.model_name or Path(args.model_name).exists():
        # ローカルチェックポイントの場合
        tokenizer = AutoTokenizer.from_pretrained(
            args.model_name, trust_remote_code=True
        )
    else:
        # Hugging Faceモデルの場合
        tokenizer = AutoTokenizer.from_pretrained(
            args.model_name, trust_remote_code=True
        )

    # パディングトークンの設定
    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "<|pad|>"})

    # 推論時は左パディング
    tokenizer.padding_side = "left"

    print(f"   Vocab size: {len(tokenizer)}")
    print(f"   Pad token: {tokenizer.pad_token} (ID: {tokenizer.pad_token_id})")
    print(f"   Padding side: {tokenizer.padding_side}")

    # モデルのロード
    print(f"\n📥 モデルをロード中: {args.model_name}")
    try:
        import torch

        model = AutoModelForCausalLM.from_pretrained(
            args.model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        )
        model.eval()
    except ImportError:
        # torchがインポートできない場合は通常の読み込み
        model = AutoModelForCausalLM.from_pretrained(
            args.model_name,
            device_map="auto",
            trust_remote_code=True,
        )

    # データセットのロード
    print(f"\n📊 データセットをロード中: {args.dataset_name}")
    dataset = load_dataset(args.dataset_name, args.dataset_config, split="test")

    # サンプル数の制限
    if args.num_samples > 0:
        dataset = dataset.select(range(min(args.num_samples, len(dataset))))

    print(f"✅ 評価サンプル数: {len(dataset)}")

    # 推論の実行
    print(f"\n🚀 推論を開始します（バッチサイズ: {args.batch_size}）...")

    samples = []
    correct_count = 0

    for batch_start in tqdm(range(0, len(dataset), args.batch_size), desc="推論中"):
        batch_end = min(batch_start + args.batch_size, len(dataset))
        batch = dataset[batch_start:batch_end]

        questions = batch["question"]
        answers_gt = batch["answer"]

        # プロンプトの作成
        prompts = [f"Q: {q}\nA:" for q in questions]

        # トークナイズ
        inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(model.device)

        # 生成
        try:
            import torch

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=100,
                    num_return_sequences=1,
                    pad_token_id=tokenizer.pad_token_id,
                    do_sample=False,
                    temperature=0.1,
                )
        except ImportError:
            # torchがインポートできない場合
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                num_return_sequences=1,
                pad_token_id=tokenizer.pad_token_id,
                do_sample=False,
                temperature=0.1,
            )

        # デコード
        generated_texts = tokenizer.batch_decode(outputs, skip_special_tokens=True)

        # 結果の処理
        for question, answer_gt, generated_text in zip(
            questions, answers_gt, generated_texts
        ):
            # 回答部分の抽出
            if "\nA:" in generated_text:
                answer_pred = generated_text.split("\nA:")[-1].strip()
            else:
                answer_pred = generated_text.strip()

            # 正解判定（簡易的な文字列比較）
            is_correct = answer_gt.lower().strip() in answer_pred.lower()
            if is_correct:
                correct_count += 1

            samples.append(
                {
                    "question": question,
                    "answer_gt": answer_gt,
                    "answer_pred": answer_pred,
                    "is_correct": is_correct,
                }
            )

    # 精度の計算
    accuracy = correct_count / len(samples) * 100 if samples else 0

    # 結果の表示
    print(f"\n📊 評価結果:")
    print(f"   正解数: {correct_count}/{len(samples)}")
    print(f"   精度: {accuracy:.2f}%")

    # 結果の保存
    # 統計情報
    stats_filename = f"eval_stats_{model_basename}_n{len(samples)}.txt"
    stats_filepath = output_dir / stats_filename
    with open(stats_filepath, "w", encoding="utf-8") as f:
        f.write(f"Model: {args.model_name}\n")
        f.write(f"Correct: {correct_count}/{len(samples)}\n")
        f.write(f"Accuracy: {accuracy:.2f}%\n")
    print(f"\n   統計情報を保存: {stats_filepath}")

    # サンプル詳細
    samples_filename = f"eval_samples_{model_basename}_n{len(samples)}.json"
    samples_filepath = output_dir / samples_filename
    with open(samples_filepath, "w", encoding="utf-8") as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    print(f"   サンプル詳細を保存: {samples_filepath}")

    # サンプル例の表示
    print("\n--- サンプル例 ---")
    for i, ex in enumerate(samples[: args.num_example_to_show]):
        print(f"\n例 {i+1}:")
        print(f"  Q: {ex['question']}")
        print(f"  A (正解): {ex['answer_gt']}")
        print(f"  A (予測): {ex['answer_pred']}")
        print(f"  正解: {'✓' if ex['is_correct'] else '✗'}")
    print("-" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GKDモデルの推論と評価")

    # モデル設定
    parser.add_argument("--model_name", type=str, required=True, help="評価するモデル名またはパス")

    # データセット設定
    parser.add_argument(
        "--dataset_name", type=str, default="openai/gsm8k", help="データセット名"
    )
    parser.add_argument("--dataset_config", type=str, default="main", help="データセット設定")

    # 推論設定
    parser.add_argument("--batch_size", type=int, default=4, help="バッチサイズ")
    parser.add_argument("--num_samples", type=int, default=100, help="評価サンプル数（0で全て）")
    parser.add_argument(
        "--num_example_to_show", type=int, default=10, help="表示するサンプル例の数"
    )

    # 出力設定
    parser.add_argument(
        "--output_dir", type=str, default="outputs/evaluation", help="出力ディレクトリ"
    )

    args = parser.parse_args()
    predict(args)
