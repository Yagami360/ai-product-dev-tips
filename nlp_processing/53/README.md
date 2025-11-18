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

または手動で:

```bash
uv sync --extra dev
```

### 2. 設定の確認

`train.py`の`CONFIG`辞書で以下の設定を確認・変更できます:

- **teacher_model_name**: 教師モデル（例: `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B`）
- **student_model_name**: 生徒モデル（例: `distilgpt2`）
- **dataset_name**: 訓練データセット（例: `gsm8k`）
- **temperature**: 蒸留温度（デフォルト: 2.0）
- **alpha**: Hard lossの重み（デフォルト: 0.5）
- **distill_loss_type**: 損失タイプ（`kl` または `mse`）

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

エポック数とバッチサイズをコマンドライン引数で指定できます:

```bash
# エポック数を5、バッチサイズを4に設定
uv run python train.py --num_epochs 5 --batch_size 4

# エポック数のみ変更
uv run python train.py --num_epochs 3

# バッチサイズのみ変更
uv run python train.py --batch_size 8
```

**引数:**
- `--num_epochs`: 訓練エポック数（デフォルト: 2）
- `--batch_size`: バッチサイズ（デフォルト: 2）

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

- `{output_dir}/final_model/`: 訓練済みモデルとトークナイザー
- `{output_dir}/loss_history.json`: 損失履歴とハイパーパラメータ
- `{output_dir}/logs/`: TensorBoardログ

## TensorBoardでの可視化

```bash
tensorboard --logdir {output_dir}/logs
```

## 注意事項

- GPUメモリが不足する場合は、`batch_size`や`gradient_accumulation_steps`を調整してください
- 教師モデルは4bit量子化でロードされます（bitsandbytesが必要）
- 大規模なモデルを使用する場合は、適切なGPU環境を用意してください

## 参考資料

- [HuggingFace Transformers Documentation](https://huggingface.co/docs/transformers)
- [Knowledge Distillation Paper](https://arxiv.org/abs/1503.02531)
