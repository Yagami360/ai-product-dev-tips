"""SensorLLM Stage2（タスク適応チューニング）の推論スクリプト。

Stage2 モデル（SensorLLMStage2LlamaForSequenceClassification）に、MHealth の
マルチチャネル・センサー窓（15ch × 100 点）を入力し、行動認識（HAR）の 12 クラス
分類を行う。学習時（train.py）と同じ前処理・トークナイズ・モデル初期化フローに
準拠し、公式のデータモジュール `make_ts_classification_data_module_stage2` を
そのまま再利用する（＝独自実装によるズレを避ける）。

Stage2 は 2 段学習（Stage1 アラインメント → Stage2 分類チューニング）が前提のため、
学習済み Stage2 チェックポイント（--model-path、既定 ./out_stage2）が必要。
"""
import os
import re
import types
import argparse

import yaml
import torch

# SensorLLM 本体（イメージ内 /opt/SensorLLM に PYTHONPATH 設定済み）
from sensorllm.model import SensorLLMStage2LlamaForSequenceClassification
from sensorllm.model.chronos_model import ChronosConfig
from sensorllm.data import make_ts_classification_data_module_stage2
from transformers import AutoConfig, AutoTokenizer

DTYPE_MAP = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}
# モデル本体（/opt/SensorLLM/sensorllm/model/ts_backbone.yaml）から id2label を引く
TS_BACKBONE_YAML = os.path.join(
    os.path.dirname(__import__("sensorllm").model.__file__), "ts_backbone.yaml"
)


def build_data_args(args, ts_backbone_config):
    """公式データモジュールが参照する DataArguments 相当の名前空間を組み立てる。

    分類データセット（MultiChannelTimeSeriesCLSDatasetStage2）は train/eval 両方を
    生成するため、train パスも渡す必要がある（本推論では eval 側のみ使用）。
    """
    return types.SimpleNamespace(
        dataset=args.dataset,
        preprocess_type=args.preprocess_type,
        preprocess_type_eval=args.preprocess_type,
        shuffle=args.shuffle,
        add_ts_special_token_text=False,
        data_path=os.path.join(args.data_dir, "train", f"{args.dataset}_train_data_stage2.pkl"),
        qa_path=os.path.join(args.data_dir, "train", f"{args.dataset}_train_qa_stage2_cls.json"),
        eval_data_path=os.path.join(args.data_dir, "test", f"{args.dataset}_test_data_stage2.pkl"),
        eval_qa_path=os.path.join(args.data_dir, "test", f"{args.dataset}_test_qa_stage2_cls.json"),
        ts_backbone_config=ts_backbone_config,
    )


def load_model(args, dtype):
    """Stage2 分類モデル・トークナイザ・Chronos トークナイザをロード（train.py 準拠）。"""
    with open(TS_BACKBONE_YAML, "r") as f:
        dataset_config = yaml.safe_load(f)[args.dataset]
    id2label = {int(k): v for k, v in dataset_config["id2label"].items()}
    label2id = {v: k for k, v in id2label.items()}
    assert args.num_labels == len(id2label), "num_labels と id2label の数が不一致"

    model = SensorLLMStage2LlamaForSequenceClassification.from_pretrained(
        args.model_path, num_labels=args.num_labels,
        id2label=id2label, label2id=label2id, torch_dtype=dtype,
    )
    model.config.use_cache = False

    # Chronos（時系列エンコーダ）バックボーンとそのトークナイザ
    model.get_model().load_pt_encoder_backbone_checkpoint(
        args.chronos_path, tc=args.tokenize_method
    )
    pt_backbone_config = AutoConfig.from_pretrained(args.chronos_path)
    chronos_config = ChronosConfig(**pt_backbone_config.chronos_config)
    chronos_config.tokenizer_class = args.tokenize_method
    chronos_tokenizer = chronos_config.create_tokenizer()

    model.get_model().fix_ts_encoder = True

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path, model_max_length=args.model_max_length,
        padding_side="right", use_fast=False,
    )

    # Stage2 は Stage1 学習済み埋め込みを引き継ぐため wo_embedding 版で初期化
    # （train.py 同様、トップレベルモデル側のメソッドを呼ぶ）
    model.initialize_tokenizer_ts_backbone_config_wo_embedding(
        tokenizer=tokenizer, dataset=args.dataset
    )
    model.get_model().load_start_end_tokens(dataset=args.dataset)

    ts_backbone_config = model.get_model().ts_backbone_config
    model = model.to(args.device).eval()
    return model, tokenizer, chronos_tokenizer, ts_backbone_config, label2id, id2label


@torch.inference_mode()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", default="./out_stage2", help="学習済み Stage2 ckpt")
    ap.add_argument("--chronos-path", default="./chronos_t5_base")
    ap.add_argument("--data-dir", default="./whole_data", help="Stage2 データ生成先")
    ap.add_argument("--dataset", default="mhealth")
    ap.add_argument("--tokenize-method", default="StanNormalizeUniformBins")
    ap.add_argument("--preprocess-type", default="smry+Q")
    ap.add_argument("--num-labels", type=int, default=12)
    ap.add_argument("--num-samples", type=int, default=8, help="推論する test サンプル数")
    ap.add_argument("--model-max-length", type=int, default=4096)
    ap.add_argument("--shuffle", dest="shuffle", action="store_true", default=True,
                    help="クラスが偏らないよう固定シードでシャッフル（既定 True）")
    ap.add_argument("--no-shuffle", dest="shuffle", action="store_false")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16", choices=list(DTYPE_MAP))
    ap.add_argument("--plot", default=None,
                    help="指定パスに、各サンプルのセンサー窓＋true/pred を並べたグリッド図を保存")
    args = ap.parse_args()

    dtype = DTYPE_MAP[args.dtype]
    model, tokenizer, chronos_tokenizer, ts_backbone_config, label2id, id2label = load_model(args, dtype)

    data_args = build_data_args(args, ts_backbone_config)
    data_module = make_ts_classification_data_module_stage2(
        tokenizer=tokenizer, chronos_tokenizer=chronos_tokenizer,
        label2id=label2id, data_args=data_args,
    )
    eval_dataset = data_module["eval_dataset"]
    collator = data_module["data_collator"]

    n = min(args.num_samples, len(eval_dataset))
    print(f"\nStage2 HAR 分類推論: test から {n} サンプル（全 {len(eval_dataset)} 件）\n")

    correct = 0
    results = []  # (i, pred_id, true_id, ok) — --plot 用
    for i in range(n):
        batch = collator([eval_dataset[i]])
        true_id = int(batch["labels"][0])
        inputs = {
            "input_ids": batch["input_ids"].to(args.device),
            "attention_mask": batch["attention_mask"].to(args.device),
            "mts_token_ids": batch["mts_token_ids"].to(args.device),
            "mts_attention_mask": batch["mts_attention_mask"].to(args.device),
            "mts_tokenizer_state": batch["mts_tokenizer_state"],
        }
        # 学習時（bf16）と同様 autocast 下で実行（Chronos 出力 fp32 と ts_proj bf16 の整合）
        with torch.autocast(device_type="cuda", dtype=dtype):
            logits = model(**inputs).logits  # (1, num_labels)
        pred_id = int(logits.argmax(dim=-1)[0])
        ok = pred_id == true_id
        correct += ok
        mark = "OK " if ok else "NG "
        print(f"[{i:2d}] {mark} pred={pred_id:2d} ({id2label[pred_id]})")
        print(f"          true={true_id:2d} ({id2label[true_id]})")
        results.append((i, pred_id, true_id, ok))

    print(f"\nAccuracy (先頭 {n} 件): {correct}/{n} = {correct / n:.3f}")

    if args.plot:
        save_grid_plot(eval_dataset, results, id2label, correct, n, args.plot)
        print(f"[plot] saved: {args.plot}")


def _short(label):
    """id2label のラベルから末尾の "(1 min)"/"(20x)" 等を落として短縮。"""
    return re.sub(r"\s*\(.*\)\s*$", "", label)


def save_grid_plot(eval_dataset, results, id2label, correct, n, path):
    """各サンプルの 15ch センサー窓を薄線で重ね描きし、true/pred をタイトルに表示したグリッド図。

    枠色＝正誤（緑=正解 / 赤=誤り）。生の窓は eval_dataset.ts_data[i]（C 本の長さ 100 系列）。
    """
    import math
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ncols = 4
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 2.4 * nrows))
    axes = axes.flatten() if n > 1 else [axes]

    for ax, (i, pred_id, true_id, ok) in zip(axes, results):
        window = eval_dataset.ts_data[i]  # list of C tensors (len=window_length)
        for ch in window:
            ax.plot(ch.numpy().astype("float32"), lw=0.6, alpha=0.55)
        color = "#1a7f37" if ok else "#cf222e"
        ax.set_title(f"[{i}] pred: {_short(id2label[pred_id])}\ntrue: {_short(id2label[true_id])}",
                     fontsize=8, color=color)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor(color); spine.set_linewidth(1.8)
    for ax in axes[len(results):]:
        ax.axis("off")

    # matplotlib に日本語フォントが無い環境でも化けないよう suptitle は英語
    fig.suptitle(f"SensorLLM Stage2 HAR classification "
                 f"(15ch sensor window / green=correct, red=wrong)  "
                 f"Accuracy {correct}/{n}={correct / n:.3f}", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
