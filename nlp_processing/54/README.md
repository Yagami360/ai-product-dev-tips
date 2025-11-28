# HuggingFace TRL の GKDTrainer を使用して LLM の蒸留モデル（GKD蒸留）を作成する

[HuggingFace TRL の GKDTrainer](https://huggingface.co/docs/trl/main/gkd_trainer) を使用した GKD [Generalized Knowledge Distillation] での知識蒸留の実装です。

## GKDの特徴

GKD (Generalized Knowledge Distillation) は、従来の Logit 蒸留等での知識蒸留の問題を解決する手法です：

1. **訓練と推論の分布ミスマッチを解決**: 生徒モデルが自己生成した出力に対して教師からフィードバックを受ける
2. **柔軟な損失関数**: Generalized Jensen-Shannon Divergence (JSD) を使用し、KL divergenceと逆KL divergenceの間を補間
3. **On-policy学習**: 生徒モデル自身が生成したデータで学習することで、より実用的な性能を実現

## 使用方法

### 1. 依存関係のインストール

```bash
make install
```

### 2. 学習

```bash
make train
```
デフォルトでは、以下のモデルを使用します

- 教師モデル（蒸留元モデル）: `Qwen/Qwen2-7B-Instruct`
- 生徒モデル（蒸留先モデル）: `Qwen/Qwen2-0.5B-Instruct`

訓練後、以下のファイルが生成されます:

- `{output_dir}/{exper_name}/checkpoint-*/`: 蒸留された学習済みモデルのチェックポイント
- `{output_dir}/{exper_name}/logs/`: TensorBoardログ

### 3. TensorBoardでの可視化

```bash
make tensorboard
```

### 4. 推論

- 教師モデルでの推論

  ```bash
  make predict-teacher
  ```

- 蒸留前の生徒モデルでの推論

  ```bash
  make predict-student
  ```

- 蒸留後の生徒モデルでの推論

  ```bash
  make　predict-distilled-student
  ```

## 結果

### モデルサイズ比較

- `Qwen2-7B-Instruct` => `Qwen2-0.5B-Instruct` への蒸留時

  |モデル名|サイズ|
  |---|---|
  |教師モデル（蒸留元）`Qwen/Qwen2-7B-Instruct`|14.18 GB|
  |生徒モデル（蒸留前）`Qwen/Qwen2-0.5B-Instruct`|0.92 GB|
  |生徒モデル（蒸留後）`Qwen/Qwen2-0.5B-Instruct`|0.92 GB|

- `Qwen2-7B-Instruct` => `Qwen2-1.5B-Instruct` への蒸留時

  |モデル名|サイズ|
  |---|---|
  |教師モデル（蒸留元）`Qwen/Qwen2-7B-Instruct`|14.18 GB|
  |生徒モデル（蒸留前）`Qwen/Qwen2-1.5B-Instruct`|2.87 GB|
  |生徒モデル（蒸留後）`Qwen/Qwen2-1.5B-Instruct`|2.87 GB|

### 精度比較

- `Qwen2-7B-Instruct` => `Qwen2-0.5B-Instruct` への蒸留時

  ||英語（原文）|日本語訳|
  |---|---|---|
  |入力プロンプト|Janet’s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?|ジャネットの鴨は1日に16個の卵を産みます。彼女は毎朝3個を朝食に食べ、毎日4個を使って友人のためにマフィンを焼きます。残りは毎日、新鮮な鴨の卵1個あたり2ドルでファーマーズマーケットで売ります。彼女はファーマーズマーケットで毎日何ドル稼ぎますか？|
  |正解データ|Janet sells 16 - 3 - 4 = <<16-3-4=9>>9 duck eggs a day.\nShe makes 9 * 2 = $<<9*2=18>>18 every day at the farmer’s market.\n#### 18|ジャネットは1日に16 - 3 - 4 = $<<16-3-4=9>>9$個の鴨の卵を売ります。\n彼女は毎日、9 $\times$ 2 = $\$<<9*2=18>>18$をファーマーズマーケットで稼ぎます。\n#### 18|
  |教師モデル `Qwen/Qwen2-7B-Instruct`|Janet's ducks lay 16 eggs per day.\nShe eats 3 eggs for breakfast, so she has 16 - 3 = 13 eggs left.\nShe uses 4 eggs to bake muffins for her friends, so she has 13 - 4 = 9 eggs left to sell.\nShe sells each egg for $2, so she makes 9 * $2 = $18 from selling the eggs.\nThe answer is: $18$|ジャネットの鴨は1日に16個の卵を産みます。彼女は朝食に3個の卵を食べるので、残りは $16 - 3 = 13$ 個になります。彼女は友人のためにマフィンを焼くのに4個の卵を使うので、売るために残るのは $13 - 4 = 9$ 個になります。彼女は卵を1個あたり2ドルで売るので、卵を売って $9 \times \$2 = \$18$ 稼ぎます。答えは： $\$18$ です。|
  |生徒モデル（蒸留前）`Qwen/Qwen2-0.5B-Instruct`|Janet's ducks lay an average of 15 eggs each day (since they lay 3+4=7 eggs), so that means she has 80 eggs to sell because 1,000-7 = 93.\n\nShe makes money from selling them by multiplying the number of eggs sold by the price per egg which is \\$2. So she earns \\$40 from selling the eggs.\n\nSo the answer is \\boxed{40}.||
  |生徒モデル（蒸留後）`Qwen/Qwen2-0.5B-Instruct`|Janet eats three meals a year, so she eats \\(3 \\times 52 = 152\\) meals.\nShe eats three birds of food each year, which means she eats $\\frac{3}{3} = 9$ meals.\n\nSo, she eats $150 - $9 = $71 meals to eat because 180 - 71 = 70.\n\nTherefore, she makes $70 / $7 = $10 meals to make every year at the Farmers’ Market.\n\nThe answer is 10.||

  - 教師モデルでは、正しい回答（18ドル）ができている
  - 蒸留前の生徒モデルでは、大きく間違った回答（40ドル）になっている
  - 蒸留後の生徒モデルでは、より正解に近い回答（10ドル）ができている

  > 学習に時間がかかるので、2 Epoch 学習時点での精度を検証。loss値はまだ十分に収束していないので、更に学習を進めていくと精度改善する可能性あり

- `Qwen2-7B-Instruct` => `Qwen2-1.5B-Instruct` への蒸留時

  ||英語（原文）|日本語訳|
  |---|---|---|
  |入力プロンプト|Janet’s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?|ジャネットの鴨は1日に16個の卵を産みます。彼女は毎朝3個を朝食に食べ、毎日4個を使って友人のためにマフィンを焼きます。残りは毎日、新鮮な鴨の卵1個あたり2ドルでファーマーズマーケットで売ります。彼女はファーマーズマーケットで毎日何ドル稼ぎますか？|
  |正解データ|Janet sells 16 - 3 - 4 = <<16-3-4=9>>9 duck eggs a day.\nShe makes 9 * 2 = $<<9*2=18>>18 every day at the farmer’s market.\n#### 18|ジャネットは1日に16 - 3 - 4 = $<<16-3-4=9>>9$個の鴨の卵を売ります。\n彼女は毎日、9 $\times$ 2 = $\$<<9*2=18>>18$をファーマーズマーケットで稼ぎます。\n#### 18|
  |教師モデル `Qwen/Qwen2-7B-Instruct`|Janet's ducks lay 16 eggs per day.\nShe eats 3 eggs for breakfast, so she has 16 - 3 = 13 eggs left.\nShe uses 4 eggs to bake muffins for her friends, so she has 13 - 4 = 9 eggs left to sell.\nShe sells each egg for $2, so she makes 9 * $2 = $18 from selling the eggs.\nThe answer is: $18$|ジャネットの鴨は1日に16個の卵を産みます。彼女は朝食に3個の卵を食べるので、残りは $16 - 3 = 13$ 個になります。彼女は友人のためにマフィンを焼くのに4個の卵を使うので、売るために残るのは $13 - 4 = 9$ 個になります。彼女は卵を1個あたり2ドルで売るので、卵を売って $9 \times \$2 = \$18$ 稼ぎます。答えは： $\$18$ です。|
  |生徒モデル（蒸留前）`Qwen/Qwen2-1.5B-Instruct`|||
  |生徒モデル（蒸留後）`Qwen/Qwen2-1.5B-Instruct`|||
