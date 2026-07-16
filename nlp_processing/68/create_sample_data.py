"""
実センサーデータ(MHealth)から Stage1 推論用の 1 チャネル分サンプルを作るスクリプト。

SensorLLM(1EE1 ckpt)は MHealth データセットで学習されているため、in-distribution な
実データを与える。ここでは MHealth の「胸部加速度 x 軸（chest acc X = チャネル c_acc_x）」を、
歩行(Walking, ラベル4)区間から 200 サンプル(50Hz→4秒)抜き出して sample_c_acc_x.npy に保存する。

MHealth のカラム構成（公式データセット説明より、0 始まり）:
  0-2  : chest acc (x,y,z)
  3-4  : ECG
  5-7  : left-ankle acc / 8-10: gyro / 11-13: mag
  14-16: right-lower-arm acc / 17-19: gyro / 20-22: mag
  23   : ラベル(0=null, 1..12 の活動)
活動ラベル: 1 立位, 2 座位, 3 臥位, 4 歩行, 5 階段, ... 10 ジョギング, 11 ランニング 等。
"""

import io
import os
import urllib.request
import zipfile

import numpy as np

URL = "https://archive.ics.uci.edu/static/public/319/mhealth+dataset.zip"
# バイナリ出力は git 管理外の outputs/ 以下に置く（推論結果 npz と同様）
OUT = os.environ.get("SAMPLE_OUT", "outputs/sample_c_acc_x.npy")
SEG_LEN = 200  # 50Hz × 4 秒
COL_CHEST_ACC_X = 0  # c_acc_x に対応
COL_LABEL = 23
ACTIVITY_WALKING = 4


def main():
    if os.path.exists(OUT):
        print(f"[INFO] {OUT} は既に存在。スキップ。")
        return

    print(f"[INFO] MHealth データセットを取得: {URL}")
    with urllib.request.urlopen(URL, timeout=120) as r:
        zbytes = r.read()

    with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
        name = next(n for n in z.namelist() if n.endswith("mHealth_subject1.log"))
        raw = z.read(name).decode("utf-8", "ignore")

    data = np.array([[float(v) for v in line.split()] for line in raw.strip().splitlines()])
    labels = data[:, COL_LABEL].astype(int)

    idx = np.where(labels == ACTIVITY_WALKING)[0]
    if len(idx) < SEG_LEN:
        raise RuntimeError("Walking 区間が短すぎます")
    start = idx[0]
    seg = data[start : start + SEG_LEN, COL_CHEST_ACC_X].astype(np.float32)

    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    np.save(OUT, seg)
    print(f"[INFO] 保存: {OUT}  ({len(seg)} samples, chest acc X = c_acc_x, " f"activity=Walking, 50Hz, subject1)")


if __name__ == "__main__":
    main()
