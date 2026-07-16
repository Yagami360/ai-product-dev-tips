"""SensorLLM Stage2（HAR 分類）推論結果の作図スクリプト。

`predict_stage2.py --save-results` が出力した npz（センサー窓 + pred/true）を読み込み、
図だけを生成する。**推論・モデル読込は行わない**ため torch / sensorllm には依存せず、
numpy + matplotlib だけで動く（GPU 不要・CPU で数秒）。

使い方:
    # 1 サンプル 1 枚の詳細図（15ch グリッド）＋ 表用サムネイル（thumbs/）を出力
    python plot_stage2.py --from-results outputs/predict_stage2_results.npz \
        --plot-dir outputs/plots/stage2_samples
    # 全サンプルを 1 枚に並べたグリッド図
    python plot_stage2.py --from-results outputs/predict_stage2_results.npz \
        --plot outputs/plots/stage2_grid.png
"""

import argparse
import json
import os
import re

import numpy as np


def load_results(path):
    """predict_stage2.py の save_results で保存した npz を (samples, id2label) に復元する。

    samples: (i, window(C,L), pred_id, true_id, ok) のリスト。
    """
    d = np.load(path, allow_pickle=True)
    id2label = {int(k): v for k, v in json.loads(str(d["id2label"])).items()}
    samples = [(int(d["idxs"][k]), d["windows"][k], int(d["preds"][k]), int(d["trues"][k]), bool(d["oks"][k])) for k in range(len(d["idxs"]))]
    return samples, id2label


def _short(label):
    """id2label のラベルから末尾の "(1 min)"/"(20x)" 等を落として短縮。"""
    return re.sub(r"\s*\(.*\)\s*$", "", label)


# 身体 3 箇所の「加速度の大きさ |acc|=sqrt(x^2+y^2+z^2)」の 3 本線用。チャネル順は
# create_dataset_stage2.py の pkl 列順に一致（胸 acc=0..2 / 左足首 acc=3..5・gyro=6..8 /
# 右前腕 acc=9..11・gyro=12..14）。
MHEALTH_ACC_MAG = [
    ("Chest |acc|", "#1f77b4", (0, 1, 2)),
    ("L-ankle |acc|", "#2ca02c", (3, 4, 5)),
    ("R-arm |acc|", "#d62728", (9, 10, 11)),
]

# MHealth 15ch のレイアウト: 行=身体部位×センサー種別（5）× 列=軸 X/Y/Z（3）。
MHEALTH_CH_ROWS = [
    ("Chest acc", "m/s^2", "#1f77b4", (0, 1, 2)),
    ("L-ankle acc", "m/s^2", "#2ca02c", (3, 4, 5)),
    ("L-ankle gyro", "deg/s", "#ff7f0e", (6, 7, 8)),
    ("R-arm acc", "m/s^2", "#9467bd", (9, 10, 11)),
    ("R-arm gyro", "deg/s", "#d62728", (12, 13, 14)),
]
_AXES = ["X", "Y", "Z"]


def _acc_magnitudes(window, is_mhealth):
    """(ラベル, 色, 系列) のリスト。window は (C, L) の np 配列。

    MHealth は身体 3 箇所の |acc|=sqrt(x^2+y^2+z^2)、それ以外は先頭 1ch をそのまま返す。
    """
    if not is_mhealth:
        return [("ch0", "#1f77b4", window[0])]
    return [(name, color, np.sqrt(sum(window[j] ** 2 for j in idx))) for name, color, idx in MHEALTH_ACC_MAG]


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
        fig.patch.set_edgecolor(edge)
        fig.patch.set_linewidth(4)
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        p = os.path.join(out_dir, f"stage2_sample_{i:02d}_{mark}.png")
        fig.savefig(p, dpi=110, bbox_inches="tight", edgecolor=edge)
        plt.close(fig)
        paths.append(p)
    return paths


def save_thumb_plots(samples, out_dir):
    """1 サンプルにつき 1 枚のコンパクトな波形サムネイルを保存（README の表の「入力波形」列用）。

    身体 3 箇所の |acc|=sqrt(x^2+y^2+z^2) を 1 枚に重ねただけの小さな図。pred/true や正誤の
    注釈は付けない（表の他列が担うため）。samples: (i, window(C,L), pred_id, true_id, ok) のリスト。
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)
    is_mhealth = samples[0][1].shape[0] == 15
    paths = []
    for i, window, _pred_id, _true_id, _ok in samples:
        fig, ax = plt.subplots(figsize=(2.2, 1.1))
        for _, color, series in _acc_magnitudes(window, is_mhealth):
            ax.plot(series, lw=1.0, color=color)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_edgecolor("#d0d7de")
        fig.tight_layout(pad=0.2)
        p = os.path.join(out_dir, f"stage2_sample_{i:02d}_wave.png")
        fig.savefig(p, dpi=110, bbox_inches="tight")
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-results", required=True, help="predict_stage2.py --save-results が出力した npz")
    ap.add_argument("--plot-dir", default=None, help="1 サンプル 1 枚の詳細図＋表用サムネイル(thumbs/)を出力")
    ap.add_argument("--plot", default=None, help="全サンプルを 1 枚に並べたグリッド図の保存先")
    args = ap.parse_args()

    samples, id2label = load_results(args.from_results)
    n = len(samples)
    correct = sum(1 for s in samples if s[4])
    print(f"[plot] {args.from_results} から {n} サンプルを読み込み（推論スキップ）。Accuracy: {correct}/{n} = {correct / n:.3f}")

    if not args.plot_dir and not args.plot:
        raise SystemExit("--plot-dir か --plot のどちらかを指定してください")

    if args.plot_dir:
        paths = save_single_plots(samples, id2label, args.plot_dir)
        print(f"[plot] saved {len(paths)} per-sample figures under: {args.plot_dir}")
        thumbs = save_thumb_plots(samples, os.path.join(args.plot_dir, "thumbs"))
        print(f"[plot] saved {len(thumbs)} waveform thumbnails under: {os.path.join(args.plot_dir, 'thumbs')}")
    if args.plot:
        save_grid_plot(samples, id2label, correct, n, args.plot)
        print(f"[plot] saved grid figure: {args.plot}")


if __name__ == "__main__":
    main()
