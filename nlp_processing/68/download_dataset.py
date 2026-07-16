"""データセットを datasets/ 配下へダウンロードするスクリプト。

使い方:
    python download_dataset.py mhealth   # MHealth を datasets/MHEALTHDATASET/ へ
    python download_dataset.py nab        # NAB の該当 CSV を datasets/nab/ へ

いずれも既に存在すればスキップする。学習データ生成（create_dataset_stage*.py）は
MHealth が未取得なら自身で DL するが、このスクリプトで事前取得しておくこともできる。
"""

import io
import os
import sys
import urllib.request
import zipfile

MHEALTH_URL = "https://archive.ics.uci.edu/static/public/319/mhealth+dataset.zip"
# NAB（Numenta Anomaly Benchmark）: Stage1 の out-of-domain デモ(C)で使う 2 系列
NAB_BASE = "https://raw.githubusercontent.com/numenta/NAB/master/data/"
NAB_FILES = {
    "ec2_cpu_utilization_5f5533.csv": "realAWSCloudwatch/ec2_cpu_utilization_5f5533.csv",
    "machine_temperature_system_failure.csv": "realKnownCause/machine_temperature_system_failure.csv",
}


def download_mhealth():
    os.makedirs("datasets", exist_ok=True)
    if os.path.isdir("datasets/MHEALTHDATASET"):
        print("[skip] datasets/MHEALTHDATASET は既に存在")
        return
    print(f"[download] {MHEALTH_URL}", flush=True)
    with urllib.request.urlopen(MHEALTH_URL, timeout=180) as r:
        zipfile.ZipFile(io.BytesIO(r.read())).extractall("datasets")
    print("[done] datasets/MHEALTHDATASET")


def download_nab():
    os.makedirs("datasets/nab", exist_ok=True)
    for name, path in NAB_FILES.items():
        dst = os.path.join("datasets/nab", name)
        if os.path.exists(dst):
            print(f"[skip] {dst}")
            continue
        print(f"[download] {NAB_BASE + path}", flush=True)
        urllib.request.urlretrieve(NAB_BASE + path, dst)
    print("[done] datasets/nab")


DATASETS = {"mhealth": download_mhealth, "nab": download_nab}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "mhealth"
    if which not in DATASETS:
        raise SystemExit(f"unknown dataset '{which}' (choose from: {', '.join(DATASETS)})")
    DATASETS[which]()
