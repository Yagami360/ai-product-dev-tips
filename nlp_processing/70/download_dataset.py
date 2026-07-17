"""NAB のセンサーデータ・既知異常区間ラベルを data/ に取得する。

検知スクリプトは初回実行時に自動ダウンロードするため必須ではないが、
事前にまとめて取得しておきたい場合に使う（オフライン実行の準備など）。
"""

import argparse

import nab_common as nab

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--nab-key", type=str, default="all", help="取得するセンサー（既定 all = プリセット全件）")
    args = parser.parse_args()

    keys = list(nab.NAB_PRESETS) if args.nab_key == "all" else [args.nab_key]
    for key in keys:
        series, timestamps, gt_windows = nab.load_nab_dataset(key)
        print(f"[data] {key}: {len(series)} 点, 既知異常区間 {len(gt_windows)} 個")
