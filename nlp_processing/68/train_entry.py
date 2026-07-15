"""SensorLLM 学習エントリ（flash-attn 不要版）。

公式の学習エントリ `train_mem.py` は先頭で flash-attn のモンキーパッチを強制 import するため、
flash-attn 未導入の環境では import 時に落ちる。flash-attn のビルドは重い（要 nvcc）ので、
本 Tip では `train.py` の `train()` を直接呼ぶ（＝flash パッチ無し、標準 attention で学習）。
学習速度は落ちるが、追加ビルド無しで学習が回る。高速化したい場合は flash-attn を導入して
`train_mem.py` を使うこと。

なお `train.py` は相対パスで `./sensorllm/model/ts_backbone.yaml` と `../metrics/*` を開くため、
SensorLLM リポジトリのルート（既定 /opt/SensorLLM）へ chdir してから起動する。これにより
`uv run` は /app（pyproject.toml のある場所）から呼べる＝正しい venv を使える。
データ/出力パスは絶対パスで渡すこと。
"""
import os

# SensorLLM リポジトリのルートへ移動（相対 yaml / ../metrics 参照のため）
SENSORLLM_ROOT = os.environ.get("SENSORLLM_ROOT", "/opt/SensorLLM")
os.chdir(SENSORLLM_ROOT)

from sensorllm.train.train import train

if __name__ == "__main__":
    train()
