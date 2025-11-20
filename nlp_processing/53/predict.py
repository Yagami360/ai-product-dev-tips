import argparse
import json
import os

import torch
from datasets import load_dataset
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer


def predict(args):
    print("\n" + "=" * 60)
    print("モデル推論と性能評価")
    print("=" * 60)

    # トークナイザーのロード
    print("\n📥 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        args.teacher_model_name,
        trust_remote_code=True,
    )
    tokenizer.pad_token = tokenizer.eos_token

    # モデルのロード
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    model.eval()

    # データセット準備
    print(f"\n📊 Loading dataset: GSM8K (test split)")
    dataset = load_dataset("gsm8k", "main", split=f"test[:{args.num_samples}]")
    print(f"✅ Dataset loaded: {len(dataset)} samples")

    correct_predictions = 0
    total_predictions = 0
    samples = []

    print(f"\n🚀 Starting inference with batch size {args.batch_size}...")

    # バッチ推論
    for batch_start in tqdm(range(0, len(dataset), args.batch_size), desc="Inferring"):
        batch_end = min(batch_start + args.batch_size, len(dataset))
        batch = dataset[batch_start:batch_end]

        questions = batch["question"]
        answers_gt = batch["answer"]

        # バッチのプロンプトを作成
        prompts = [f"Q: {q}\nA:" for q in questions]

        # バッチトークナイズ
        inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        ).to(model.device)

        # バッチ推論
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=False,
            )

        # バッチデコード
        generated_texts = tokenizer.batch_decode(outputs, skip_special_tokens=True)

        # 各サンプルの結果を処理
        for question, answer_gt, generated_text in zip(questions, answers_gt, generated_texts):
            # 回答部分を抽出
            # モデルの出力が "Q: ... A: {answer}" の形式であることを期待
            if "\nA:" in generated_text:
                answer_pred_raw = generated_text.split("\nA:", 1)[1].strip()
            else:
                answer_pred_raw = generated_text.strip()

            # ここでは簡易的な評価を行う。より厳密な評価は別途実装
            # 正解の answer が含まれているかをチェックする
            is_correct = answer_gt.lower() in answer_pred_raw.lower()
            if is_correct:
                correct_predictions += 1
            total_predictions += 1

            samples.append(
                {
                    "question": question,
                    "answer_gt": answer_gt,
                    "answer_pred": answer_pred_raw,
                    "is_correct": is_correct,
                }
            )

    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
    print(f"\n✅ Inference complete!")
    print(f"   Correct predictions: {correct_predictions}")
    print(f"   Total predictions:   {total_predictions}")
    print(f"   Accuracy:            {accuracy:.2f}%")

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        model_basename = os.path.basename(args.model_name.replace("/", "_"))
        output_filename = f"eval_stats_{model_basename}_n{args.num_samples}.txt"
        output_filepath = os.path.join(args.output_dir, output_filename)

        with open(output_filepath, "w") as f:
            f.write(f"Correct predictions: {correct_predictions}\n")
            f.write(f"Total predictions:   {total_predictions}\n")
            f.write(f"Accuracy:            {accuracy:.2f}%\n")

        samples_filename = f"eval_samples_{model_basename}_n{args.num_samples}.json"
        samples_filepath = os.path.join(args.output_dir, samples_filename)
        with open(samples_filepath, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=4)
        print(f"   Evaluation Samples saved to:   {samples_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Model Inference and Evaluation")
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2-7B-Instruct")
    parser.add_argument("--teacher_model_name", type=str, default="Qwen/Qwen2-7B-Instruct")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--num_samples", type=int, default=20)
    args = parser.parse_args()

    predict(args)
