# HuggingFace Transformers の カスタム Trainer を使用して LLM の蒸留モデル（Logit蒸留）を作成する

このプロジェクトは、HuggingFace TransformersのカスタムTrainerを使用して、大規模な教師モデルから小規模な生徒モデルへ知識を蒸留する実装です。

## 特徴

- **Logit蒸留**: 教師モデルの出力ロジットから生徒モデルへ知識を転移
- **KL Divergence損失**: 標準的な知識蒸留損失関数
- **Hard/Soft損失の組み合わせ**: クロスエントロピー損失と蒸留損失のバランス調整
- **温度スケーリング**: ソフトな確率分布による効果的な知識転移
- **メモリ効率**: 4bit量子化、勾配チェックポイント、混合精度訓練をサポート

## セットアップ

### 1. 依存関係のインストール

```bash
make install
```

`make install`を実行すると、自動的にGPUの有無を検出します:
- **GPU検出時**: `bitsandbytes`を含むすべての依存関係をインストール
- **GPU未検出時**: `bitsandbytes`をスキップしてインストール

手動でインストールする場合:

```bash
# GPUありの場合
uv sync --extra dev --extra gpu

# GPUなしの場合
uv sync --extra dev
```

### 2. 設定の確認

`train.py`のコマンドライン引数で以下の設定を確認・変更できます:

- **exper_name**: 実験名（デフォルト: `qwen2-7b-to-qwen2-0.5b-distill-20251119`）
- **teacher_model_name**: 教師モデル（デフォルト: `Qwen/Qwen2-7B-Instruct`）
- **student_model_name**: 生徒モデル（デフォルト: `Qwen/Qwen2-0.5B-Instruct`）
- **num_epochs**: 訓練エポック数（デフォルト: 100）
- **batch_size**: バッチサイズ（デフォルト: 4）
- **distillation_logit_temperature**: 蒸留温度（デフォルト: 2.0）
- **distillation_logit_alpha**: Hard lossの重み（デフォルト: 0.5）
- **use_4bit**: 教師モデルの4bit量子化を使用（デフォルト: True）

## 使用方法

### 訓練の実行

```bash
make train
```

または手動で:

```bash
uv run python train.py
```

### コマンドライン引数

コマンドライン引数で訓練設定をカスタマイズできます:

```bash
# 実験名、エポック数、バッチサイズを指定
uv run python train.py --exper_name my-experiment --num_epochs 50 --batch_size 8

# エポック数のみ変更
uv run python train.py --num_epochs 50

# バッチサイズのみ変更
uv run python train.py --batch_size 8

# 教師モデルと生徒モデルを変更
uv run python train.py --teacher_model_name Qwen/Qwen2-1.5B-Instruct --student_model_name distilgpt2
```

**主要な引数:**
- `--exper_name`: 実験名（デフォルト: `qwen2-7b-to-qwen2-0.5b-distill-20251119`）
- `--num_epochs`: 訓練エポック数（デフォルト: 100）
- `--batch_size`: バッチサイズ（デフォルト: 4）
- `--teacher_model_name`: 教師モデル名（デフォルト: `Qwen/Qwen2-7B-Instruct`）
- `--student_model_name`: 生徒モデル名（デフォルト: `Qwen/Qwen2-0.5B-Instruct`）
- `--distillation_logit_temperature`: 蒸留温度（デフォルト: 2.0）
- `--distillation_logit_alpha`: Hard lossの重み（デフォルト: 0.5）
- `--use_4bit`: 教師モデルの4bit量子化を使用（デフォルト: True）
- `--output_dir`: 出力ディレクトリ（デフォルト: `outputs`）
- `--logging_steps`: ログ出力間隔（デフォルト: 100）
- `--save_steps`: モデル保存間隔（デフォルト: 500）

### 訓練の流れ

1. **モデルロード**: 教師モデルと生徒モデルをロード
2. **データ準備**: データセットのロードとトークン化
3. **蒸留訓練**: Logit蒸留による知識転移
4. **モデル保存**: 訓練済みモデルの保存
5. **簡易テスト**: 生成タスクでの動作確認

## カスタムTrainerの実装

`trainer.py`の`LogitDistillationTrainer`クラスは、以下の機能を提供します:

- **compute_loss**: 蒸留損失の計算
  - Hard loss: クロスエントロピー損失（正解ラベルとの差）
  - Soft loss: KL Divergence損失（教師モデルの出力との差）
  - 総損失: `alpha * hard_loss + (1 - alpha) * soft_loss`

- **save_model**: モデルと損失履歴の保存

## 出力

訓練後、以下のファイルが生成されます:

- `{output_dir}/{exper_name}/final_model/`: 訓練済みモデルとトークナイザー
- `{output_dir}/{exper_name}/logs/`: TensorBoardログ
- `{output_dir}/{exper_name}/checkpoint-*/`: 訓練チェックポイント

## TensorBoardでの可視化

```bash
tensorboard --logdir {output_dir}/{exper_name}/logs
```

## 注意事項

- **GPUメモリ**: GPUメモリが不足する場合は、`batch_size`を小さくするか、`use_4bit`を有効にして教師モデルを4bit量子化してください
- **4bit量子化**: 
  - 教師モデルは推論のみで使用するため、4bit量子化でメモリ節約が可能です
  - **生徒モデルは訓練する必要があるため、4bit量子化は使用できません**（4bit量子化されたモデルは直接ファインチューニングできません）
  - 4bit量子化を使用する場合は、GPU環境と`bitsandbytes`が必要です（`make install`で自動インストールされます）
- **混合精度訓練**: 4bit量子化を使用する場合、`fp16`は自動的に無効化されます
- **大規模モデル**: 大規模なモデルを使用する場合は、適切なGPU環境を用意してください

## 参考資料

- [HuggingFace Transformers Documentation](https://huggingface.co/docs/transformers)
- [Knowledge Distillation Paper](https://arxiv.org/abs/1503.02531)
