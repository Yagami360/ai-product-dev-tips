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
    dataset = load_dataset("gsm8k", "main", split="test")
    print(f"✅ Dataset loaded: {len(dataset)} samples")

    correct_predictions = 0
    total_predictions = 0
    examples = []

    print("\n🚀 Starting inference...")
    for i, example in enumerate(tqdm(dataset, desc="Inferring")):
        question = example["question"]
        answer_gt = example["answer"]

        prompt = f"Q: {question}\nA:"
        input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                max_new_tokens=100,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=False,
            )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # print(f"Generated text: {generated_text}")

        # 回答部分を抽出
        # モデルの出力が "Q: ... A: {answer}" の形式であることを期待
        if "\nA:" in generated_text:
            answer_pred_raw = generated_text.split("\nA:", 1)[1].strip()
        else:
            answer_pred_raw = generated_text.strip()

        # ここでは簡易的な評価を行う。より厳密な評価は別途実装
        # 正解の answer が含まれているかをチェックする
        if answer_gt.lower() in answer_pred_raw.lower():
            correct_predictions += 1
        total_predictions += 1

        if args.save_examples:
            examples.append(
                {
                    "question": question,
                    "answer_gt": answer_gt,
                    "answer_pred": answer_pred_raw,
                    "is_correct": answer_gt.lower() in answer_pred_raw.lower(),
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
        output_filename = f"{model_basename}_metrics.txt"
        output_filepath = os.path.join(args.output_dir, output_filename)

        with open(output_filepath, "w") as f:
            f.write(f"Correct predictions: {correct_predictions}\n")
            f.write(f"Total predictions:   {total_predictions}\n")
            f.write(f"Accuracy:            {accuracy:.2f}%\n")

        examples_filename = f"{model_basename}_examples.json"
        examples_filepath = os.path.join(args.output_dir, examples_filename)
        with open(examples_filepath, "w", encoding="utf-8") as f:
            json.dump(examples, f, ensure_ascii=False, indent=4)
        print(f"   Examples saved to:   {examples_filepath}")

        print("\n--- Sample Examples ---")
        for i, ex in enumerate(examples[: args.num_example_to_show]):
            print(f"\nExample {i+1}:")
            print(f"  Q: {ex['question']}")
            print(f"  A (True): {ex['answer_gt']}")
            print(f"  A (Predicted): {ex['predicted_answer']}")
            print(f"  Correct: {ex['is_correct']}")
        print("-----------------------")
        print(f"   Results saved to:    {output_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Model Inference and Evaluation")
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2-7B-Instruct")
    parser.add_argument("--teacher_model_name", type=str, default="Qwen/Qwen2-7B-Instruct")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--num_example_to_show", type=int, default=10)
    args = parser.parse_args()

    predict(args)
