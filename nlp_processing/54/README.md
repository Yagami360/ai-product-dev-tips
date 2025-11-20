# GKD (Generalized Knowledge Distillation) による知識蒸留

[HuggingFace TRL の GKDTrainer](https://huggingface.co/docs/trl/main/gkd_trainer) を使用した知識蒸留の実装です。

## GKDの特徴

GKD (Generalized Knowledge Distillation) は、従来の知識蒸留の問題を解決する手法です：

1. **訓練と推論の分布ミスマッチを解決**: 生徒モデルが自己生成した出力に対して教師からフィードバックを受ける
2. **柔軟な損失関数**: Generalized Jensen-Shannon Divergence (JSD) を使用し、KL divergenceと逆KL divergenceの間を補間
3. **On-policy学習**: 生徒モデル自身が生成したデータで学習することで、より実用的な性能を実現

## セットアップ

```bash
# 依存関係のインストール
make install
```

## 使用方法

### 基本的な訓練

```bash
# GKDによる知識蒸留の実行
make train
```

### 推論と評価

```bash
# 蒸留後のモデルで推論
make predict-student
```

### TensorBoardで訓練ログを確認

```bash
make tensorboard
```

## パラメータ説明

### GKD特有のパラメータ

- **lmbda** (0.0-1.0): 生徒データ割合
  - 0.0: 教師の確率分布で学習（supervised JSD）
  - 1.0: 生徒が生成したデータで学習（on-policy JSD）
  - 推奨値: 0.5-0.7

- **beta** (0.0-1.0): JSD補間係数
  - 0.0: Forward KL divergence
  - 1.0: Reverse KL divergence
  - 推奨値: 0.5

- **temperature**: サンプリング温度（高いほどランダム）
  - 推奨値: 0.9

- **seq_kd**: Sequence-Level KDの使用
  - True: 教師が生成した系列で学習

## ディレクトリ構造

```
54/
├── train.py          # GKD訓練スクリプト
├── predict.py        # 推論・評価スクリプト
├── utils.py          # ユーティリティ関数
├── Makefile          # タスク自動化
├── pyproject.toml    # プロジェクト設定
├── README.md         # このファイル
└── outputs/          # 出力ディレクトリ
    └── {実験名}/
        ├── checkpoint-final/  # 最終モデル
        ├── logs/             # TensorBoardログ
        └── evaluation/       # 評価結果
```

## 実験結果の例

```
=== Teacher Model (Qwen2-7B) ===
Accuracy: 75.0%

=== Student Model Before Distillation (Qwen2-0.5B) ===
Accuracy: 15.0%

=== Student Model After GKD Distillation ===
Accuracy: 45.0%
```

## 参考文献

- [On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes](https://huggingface.co/papers/2306.13649)
- [HuggingFace TRL GKDTrainer Documentation](https://huggingface.co/docs/trl/main/gkd_trainer)

## トラブルシューティング

### メモリ不足の場合

1. バッチサイズを小さくする
2. 4bit量子化を使用する（`make train-4bit`）
3. `gradient_accumulation_steps`を増やす

### 性能が向上しない場合

1. `lmbda`を高めに設定（0.7-0.9）してon-policy学習を強化
2. `temperature`を調整（0.7-1.0）
3. 学習率を調整（1e-5 - 1e-4）
