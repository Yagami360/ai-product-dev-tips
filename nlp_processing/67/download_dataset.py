"""NAB のセンサーデータ・既知異常区間ラベルを data/ に取得する。

create_report.py は初回実行時に自動ダウンロードするため必須ではないが、
事前にまとめて取得しておきたい場合に使う（オフライン実行の準備など）。
"""

import argparse

from create_report import NAB_PRESETS, load_nab_dataset

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--nab-key", type=str, default="all", help="取得するセンサー（既定 all = プリセット全件）")
    args = parser.parse_args()

    keys = list(NAB_PRESETS) if args.nab_key == "all" else [args.nab_key]
    for key in keys:
        series, xs, gt_windows = load_nab_dataset(key)
        print(f"[data] {key}: {len(series)} 点, 既知異常区間 {len(gt_windows)} 個")
