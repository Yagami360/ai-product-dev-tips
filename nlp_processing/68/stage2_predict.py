"""SensorLLM Stage2（タスク適応チューニング）の推論スクリプト。

Stage2 モデル（SensorLLMStage2LlamaForSequenceClassification）に、MHealth の
マルチチャネル・センサー窓（15ch × 100 点）を入力し、行動認識（HAR）の 12 クラス
分類を行う。学習時（train.py）と同じ前処理・トークナイズ・モデル初期化フローに
準拠し、公式のデータモジュール `make_ts_classification_data_module_stage2` を
そのまま再利用する（＝独自実装によるズレを避ける）。

Stage2 は 2 段学習（Stage1 アラインメント → Stage2 分類チューニング）が前提のため、
学習済み Stage2 チェックポイント（--model-path、既定 ./out_stage2）が必要。
"""

import argparse
import json
import os
import re
import types

import numpy as np
import torch
import yaml
from sensorllm.data import make_ts_classification_data_module_stage2

# SensorLLM 本体（イメージ内 /opt/SensorLLM に PYTHONPATH 設定済み）
from sensorllm.model import SensorLLMStage2LlamaForSequenceClassification
from sensorllm.model.chronos_model import ChronosConfig
from transformers import AutoConfig, AutoTokenizer

DTYPE_MAP = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}
# モデル本体（/opt/SensorLLM/sensorllm/model/ts_backbone.yaml）から id2label を引く
TS_BACKBONE_YAML = os.path.join(os.path.dirname(__import__("sensorllm").model.__file__), "ts_backbone.yaml")


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
        args.model_path,
        num_labels=args.num_labels,
        id2label=id2label,
        label2id=label2id,
        torch_dtype=dtype,
    )
    model.config.use_cache = False

    # Chronos（時系列エンコーダ）バックボーンとそのトークナイザ
    model.get_model().load_pt_encoder_backbone_checkpoint(args.chronos_path, tc=args.tokenize_method)
    pt_backbone_config = AutoConfig.from_pretrained(args.chronos_path)
    chronos_config = ChronosConfig(**pt_backbone_config.chronos_config)
    chronos_config.tokenizer_class = args.tokenize_method
    chronos_tokenizer = chronos_config.create_tokenizer()

    model.get_model().fix_ts_encoder = True

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path,
        model_max_length=args.model_max_length,
        padding_side="right",
        use_fast=False,
    )

    # Stage2 は Stage1 学習済み埋め込みを引き継ぐため wo_embedding 版で初期化
    # （train.py 同様、トップレベルモデル側のメソッドを呼ぶ）
    model.initialize_tokenizer_ts_backbone_config_wo_embedding(tokenizer=tokenizer, dataset=args.dataset)
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
    ap.add_argument("--shuffle", dest="shuffle", action="store_true", default=True, help="クラスが偏らないよう固定シードでシャッフル（既定 True）")
    ap.add_argument("--no-shuffle", dest="shuffle", action="store_false")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16", choices=list(DTYPE_MAP))
    ap.add_argument("--plot", default=None, help="指定パスに、全サンプルを 1 枚に並べたグリッド図を保存")
    ap.add_argument("--plot-dir", default=None, help="指定ディレクトリに、1 サンプルごとに独立した plot 図を保存")
    ap.add_argument("--save-results", default=None, help="推論結果（センサー窓＋pred/true）を npz に保存（後でモデル無しで再プロット可）")
    ap.add_argument("--from-results", default=None, help="保存済み npz からプロットのみ行う（推論・モデル読込をスキップ）")
    args = ap.parse_args()

    # --from-results 指定時は推論もモデル読込もせず、保存済み結果からプロットだけ行う
    if args.from_results:
        samples, id2label = load_results(args.from_results)
        n = len(samples)
        correct = sum(1 for s in samples if s[4])
        print(f"[from-results] {args.from_results} から {n} サンプルを読み込み（推論スキップ）")
        print(f"Accuracy: {correct}/{n} = {correct / n:.3f}")
    else:
        dtype = DTYPE_MAP[args.dtype]
        model, tokenizer, chronos_tokenizer, ts_backbone_config, label2id, id2label = load_model(args, dtype)

        data_args = build_data_args(args, ts_backbone_config)
        data_module = make_ts_classification_data_module_stage2(
            tokenizer=tokenizer,
            chronos_tokenizer=chronos_tokenizer,
            label2id=label2id,
            data_args=data_args,
        )
        eval_dataset = data_module["eval_dataset"]
        collator = data_module["data_collator"]

        n = min(args.num_samples, len(eval_dataset))
        print(f"\nStage2 HAR 分類推論: test から {n} サンプル（全 {len(eval_dataset)} 件）\n")

        correct = 0
        samples = []  # (i, window(C,L), pred_id, true_id, ok)
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
            window = np.stack([ch.numpy().astype("float32") for ch in eval_dataset.ts_data[i]])  # (C, L)
            samples.append((i, window, pred_id, true_id, bool(ok)))

        print(f"\nAccuracy (先頭 {n} 件): {correct}/{n} = {correct / n:.3f}")

        if args.save_results:
            save_results(args.save_results, samples, id2label)
            print(f"[results] saved: {args.save_results}（--from-results で再プロット可）")

    if args.plot:
        save_grid_plot(samples, id2label, correct, n, args.plot)
        print(f"[plot] saved: {args.plot}")
    if args.plot_dir:
        paths = save_single_plots(samples, id2label, args.plot_dir)
        print(f"[plot] saved {len(paths)} per-sample figures under: {args.plot_dir}")


def save_results(path, samples, id2label):
    """推論結果を npz に保存（windows/idxs/preds/trues/oks + id2label(JSON)）。"""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    np.savez_compressed(
        path,
        windows=np.stack([s[1] for s in samples]),  # (N, C, L)
        idxs=np.array([s[0] for s in samples]),
        preds=np.array([s[2] for s in samples]),
        trues=np.array([s[3] for s in samples]),
        oks=np.array([s[4] for s in samples], dtype=bool),
        id2label=json.dumps({int(k): v for k, v in id2label.items()}, ensure_ascii=False),
    )


def load_results(path):
    """save_results で保存した npz を (samples, id2label) に復元する。"""
    d = np.load(path, allow_pickle=True)
    id2label = {int(k): v for k, v in json.loads(str(d["id2label"])).items()}
    samples = [(int(d["idxs"][k]), d["windows"][k], int(d["preds"][k]), int(d["trues"][k]), bool(d["oks"][k])) for k in range(len(d["idxs"]))]
    return samples, id2label


def _short(label):
    """id2label のラベルから末尾の "(1 min)"/"(20x)" 等を落として短縮。"""
    return re.sub(r"\s*\(.*\)\s*$", "", label)


# 15ch すべてを描くと煩雑なので、身体 3 箇所の「加速度の大きさ |acc|=sqrt(x^2+y^2+z^2)」の
# 3 本線だけを描いて分かりやすくする。チャネル順は create_stage2_dataset.py の pkl 列順に一致。
# （胸 acc=0..2 / 左足首 acc=3..5・gyro=6..8 / 右前腕 acc=9..11・gyro=12..14）
MHEALTH_ACC_MAG = [
    ("Chest |acc|", "#1f77b4", (0, 1, 2)),
    ("L-ankle |acc|", "#2ca02c", (3, 4, 5)),
    ("R-arm |acc|", "#d62728", (9, 10, 11)),
]


def _acc_magnitudes(window, is_mhealth):
    """(ラベル, 色, 系列) のリスト。window は (C, L) の np 配列。

    MHealth は身体 3 箇所の |acc|=sqrt(x^2+y^2+z^2)、それ以外は先頭 1ch をそのまま返す。
    """
    if not is_mhealth:
        return [("ch0", "#1f77b4", window[0])]
    return [(name, color, np.sqrt(sum(window[j] ** 2 for j in idx))) for name, color, idx in MHEALTH_ACC_MAG]


# MHealth 15ch のレイアウト: 行=身体部位×センサー種別（5）× 列=軸 X/Y/Z（3）。
# チャネル順は create_stage2_dataset.py の pkl 列順に一致。
MHEALTH_CH_ROWS = [
    ("Chest acc", "m/s^2", "#1f77b4", (0, 1, 2)),
    ("L-ankle acc", "m/s^2", "#2ca02c", (3, 4, 5)),
    ("L-ankle gyro", "deg/s", "#ff7f0e", (6, 7, 8)),
    ("R-arm acc", "m/s^2", "#9467bd", (9, 10, 11)),
    ("R-arm gyro", "deg/s", "#d62728", (12, 13, 14)),
]
_AXES = ["X", "Y", "Z"]


def save_single_plots(samples, id2label, out_dir):
    """1 サンプルにつき 1 枚の図を保存（図内は 15 チャネルを個別サブプロットで並べる）。

    MHealth は 行=身体部位×センサー種別（5）× 列=軸 X/Y/Z（3）の 5×3 グリッド。各サブプロット
    が 1 チャネルの 100 点時系列。図の枠色＝正誤（緑=正解 / 赤=誤り）、suptitle に pred/true。
    samples: (i, window(C,L), pred_id, true_id, ok) のリスト。
    """
    import math

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)
    is_mhealth = samples[0][1].shape[0] == 15
    paths = []
    for i, window, pred_id, true_id, ok in samples:
        edge = "#1a7f37" if ok else "#cf222e"
        mark = "OK" if ok else "NG"
        if is_mhealth:
            fig, axes = plt.subplots(5, 3, figsize=(9, 8), sharex=True)
            for r, (label, unit, color, idx) in enumerate(MHEALTH_CH_ROWS):
                for c in range(3):
                    ax = axes[r][c]
                    ax.plot(window[idx[c]], color=color, lw=1.0)
                    ax.set_title(f"{label} {_AXES[c]} ({unit})", fontsize=8)
                    ax.tick_params(labelsize=6)
                    if r == 4:
                        ax.set_xlabel("time (100=2s)", fontsize=7)
        else:  # 15ch でないデータセットは全 C チャネルを正方に近いグリッドで並べる
            C = window.shape[0]
            ncol = min(4, C)
            nrow = math.ceil(C / ncol)
            fig, axes = plt.subplots(nrow, ncol, figsize=(3 * ncol, 2 * nrow), squeeze=False)
            for k in range(nrow * ncol):
                ax = axes[k // ncol][k % ncol]
                if k < C:
                    ax.plot(window[k], lw=1.0)
                    ax.set_title(f"ch{k}", fontsize=8)
                    ax.tick_params(labelsize=6)
                else:
                    ax.axis("off")
        fig.suptitle(
            f"sample #{i}  [{mark}]   pred: {_short(id2label[pred_id])}   /   " f"true: {_short(id2label[true_id])}", fontsize=12, color=edge
        )
        for spine in fig.get_axes()[0].spines.values():
            pass  # サブプロット個別の枠は付けず、figure 全体の枠色で正誤を示す
        fig.patch.set_edgecolor(edge)
        fig.patch.set_linewidth(4)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        p = os.path.join(out_dir, f"stage2_sample_{i:02d}_{mark}.png")
        fig.savefig(p, dpi=110, bbox_inches="tight", edgecolor=edge)
        plt.close(fig)
        paths.append(p)
    return paths


def save_grid_plot(samples, id2label, correct, n, path):
    """全サンプルを 1 枚に並べたグリッド図（各パネル = 身体 3 箇所の |acc| 3 本線）。

    samples: (i, window(C,L), pred_id, true_id, ok) のリスト。
    枠色＝正誤（緑=正解 / 赤=誤り）、タイトル pred=予測 / true=正解。
    """
    import math

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    is_mhealth = samples[0][1].shape[0] == 15

    ncols = 4
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.6 * ncols, 2.3 * nrows))
    axes = axes.flatten() if n > 1 else [axes]

    for ax, (i, window, pred_id, true_id, ok) in zip(axes, samples):
        for _, color, series in _acc_magnitudes(window, is_mhealth):
            ax.plot(series, lw=1.1, color=color)
        color = "#1a7f37" if ok else "#cf222e"
        ax.set_title(f"[{i}] pred: {_short(id2label[pred_id])}\ntrue: {_short(id2label[true_id])}", fontsize=8, color=color)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor(color)
            spine.set_linewidth(1.8)
    for ax in axes[len(samples) :]:
        ax.axis("off")

    # matplotlib に日本語フォントが無い環境でも化けないよう英語表記
    fig.suptitle(
        f"SensorLLM Stage2 HAR classification  |  panel = one 2s test window; "
        f"lines = acceleration magnitude |acc| at 3 body sites; "
        f"frame green=correct / red=wrong; title pred / true  |  "
        f"Accuracy {correct}/{n}={correct / n:.3f}",
        fontsize=9,
    )
    fig.supxlabel("time (100 samples = 2 s @ 50 Hz)", fontsize=9)
    fig.supylabel("|acc| (m/s^2)", fontsize=9)
    if is_mhealth:
        handles = [Line2D([0], [0], color=c, lw=2, label=name) for name, c, _ in MHEALTH_ACC_MAG]
        fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=[0.02, 0.05, 1, 0.95])
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
