"""ローカルで動くガードレールモデルを、日本語データで CPU 実測比較する。

- タスク pi  : 日本語プロンプトインジェクション（自作 pi_ja.jsonl。直接 / 間接 / 良性 / 紛らわしい良性）
- タスク harm: 日本語の有害プロンプト（nvidia/Nemotron-Safety-Guard-Dataset-v3 の ja/test から人手ラベルのみ抽出）

どのモデルも「入力テキスト → unsafe か否か」の二値に揃えて、同じ指標で比べる。
"""

import argparse
import json
import os
import random
import re
import statistics
import time
import urllib.request

# モデル名 → (バックエンド, 実体)
#   hf-cls : transformers の text-classification（小型エンコーダ分類器）
#   hf-gen : transformers の生成型ガード（Qwen3Guard-Gen）
#   ollama : Ollama 経由の生成型ガード
MODELS = {
    "horizon-pi-guard": ("hf-cls", "Horizon-Labs/prompt-injection-guard-base"),
    "protectai-deberta-pi": ("hf-cls", "protectai/deberta-v3-base-prompt-injection-v2"),
    "qwen3guard-gen-0.6b": ("hf-gen", "Qwen/Qwen3Guard-Gen-0.6B"),
    "llama-guard3-1b": ("ollama", "llama-guard3:1b"),
    "shieldgemma-2b": ("ollama", "shieldgemma:2b"),
    "granite3-guardian-2b": ("ollama", "granite3-guardian:2b"),
}


def load_pi(path):
    with open(path) as f:
        return [json.loads(line) for line in f]


def load_harm(n, seed):
    """Nemotron-Safety-Guard-Dataset-v3 の ja/test から、人手ラベルのプロンプトを safe / unsafe 半々で n 件抽出する。"""
    from huggingface_hub import hf_hub_download

    path = hf_hub_download("nvidia/Nemotron-Safety-Guard-Dataset-v3", "ja/test.jsonl", repo_type="dataset", local_dir="datasets")
    with open(path) as f:
        rows = [json.loads(line) for line in f]
    rows = [r for r in rows if r["prompt_label_source"] == "human"]
    rng = random.Random(seed)
    data = []
    for label in ("unsafe", "safe"):
        picked = rng.sample([r for r in rows if r["prompt_label"] == label], n // 2)
        data += [{"id": r["id"], "type": label, "label": int(label == "unsafe"), "text": r["prompt"]} for r in picked]
    return data


def build_judge(name, task):
    """テキストを受け取り (unsafe か, 生の出力) を返す関数を作る。"""
    backend, target = MODELS[name]

    if backend == "hf-cls":
        from transformers import pipeline

        clf = pipeline("text-classification", model=target, device="cpu", truncation=True, max_length=512)
        # どちらのモデルもラベルは SAFE / INJECTION
        return lambda text: (lambda out: (out["label"] == "INJECTION", f"{out['label']} {out['score']:.3f}"))(clf(text)[0])

    if backend == "hf-gen":
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tok = AutoTokenizer.from_pretrained(target)
        model = AutoModelForCausalLM.from_pretrained(target, torch_dtype=torch.float32).eval()

        def judge(text):
            ids = tok.apply_chat_template([{"role": "user", "content": text}], add_generation_prompt=True, return_tensors="pt")
            with torch.no_grad():
                out = model.generate(ids, max_new_tokens=32, do_sample=False)
            content = tok.decode(out[0][ids.shape[1] :], skip_special_tokens=True)
            m = re.search(r"Safety: (Safe|Unsafe|Controversial)", content)
            # Controversial（判断が分かれる）は unsafe 側に倒す（見逃しを減らす側の設定）
            return (m is not None and m.group(1) != "Safe"), content.strip().replace("\n", " ")

        return judge

    # ollama: 各モデルの chat テンプレートがガード用プロンプトに展開してくれるので、ユーザー発話としてそのまま渡す
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    # granite3-guardian は system メッセージでリスク定義を切り替えられる（pi タスクでは jailbreak 定義を使う）
    system = [{"role": "system", "content": "jailbreak" if task == "pi" else "harm"}] if target.startswith("granite3-guardian") else []

    def judge(text):
        messages = system + [{"role": "user", "content": text}]
        body = {"model": target, "messages": messages, "stream": False, "options": {"temperature": 0}}
        req = urllib.request.Request(f"{host}/api/chat", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as res:
            content = json.load(res)["message"]["content"].strip()
        # llama-guard3 は "safe" / "unsafe\nS1"、shieldgemma と granite3-guardian は "Yes"（違反あり）/ "No"
        return content.lower().startswith(("unsafe", "yes")), content.replace("\n", " ")

    return judge


def evaluate(data, judge):
    rows, latencies = [], []
    # ウォームアップ（初回のモデルロード時間を計測に含めない）。評価データと同じ文を使うと Ollama のプロンプトキャッシュが効いてしまうので別の文にする
    judge("こんにちは")
    for d in data:
        t0 = time.perf_counter()
        pred, raw = judge(d["text"])
        latencies.append((time.perf_counter() - t0) * 1000)
        rows.append({**d, "pred": int(pred), "raw": raw, "latency_ms": round(latencies[-1], 1)})

    tp = sum(r["label"] and r["pred"] for r in rows)
    fp = sum((not r["label"]) and r["pred"] for r in rows)
    fn = sum(r["label"] and not r["pred"] for r in rows)
    tn = sum((not r["label"]) and not r["pred"] for r in rows)
    recall = tp / (tp + fn) if tp + fn else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    metrics = {
        "recall": recall,
        "precision": precision,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "fpr": fp / (fp + tn) if fp + tn else 0.0,
        "latency_p50_ms": statistics.median(latencies),
        "latency_p95_ms": statistics.quantiles(latencies, n=20)[18],
        # 種類別の「unsafe と判定した割合」（攻撃側は高いほど良く、良性側は低いほど良い）
        "flag_rate_by_type": {},
    }
    for t in dict.fromkeys(r["type"] for r in rows):
        preds = [r["pred"] for r in rows if r["type"] == t]
        metrics["flag_rate_by_type"][t] = sum(preds) / len(preds)
    return metrics, rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=["pi", "harm"], default="pi")
    parser.add_argument("--model", choices=list(MODELS), default="horizon-pi-guard")
    parser.add_argument("--pi-data", default="pi_ja.jsonl")
    parser.add_argument("--n-harm", type=int, default=200, help="harm タスクのサンプル数（safe / unsafe 半々）")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out-dir", default="results")
    args = parser.parse_args()

    data = load_pi(args.pi_data) if args.task == "pi" else load_harm(args.n_harm, args.seed)
    metrics, rows = evaluate(data, build_judge(args.model, args.task))

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(args.out_dir, f"{args.task}_{args.model}.json")
    with open(out_path, "w") as f:
        json.dump({"task": args.task, "model": args.model, "n": len(rows), "metrics": metrics, "rows": rows}, f, ensure_ascii=False, indent=2)

    print(json.dumps({"task": args.task, "model": args.model, "n": len(rows), **metrics}, ensure_ascii=False, indent=2))
    print(f"saved: {out_path}")
