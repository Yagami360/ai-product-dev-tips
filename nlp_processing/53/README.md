# HuggingFace Transformers の カスタム Trainer を使用して LLM（Qwen）の蒸留モデル（Logit蒸留）を作成する

HuggingFace Transformers のカスタムTrainerを使用した、大規模教師モデル（LLM）から小規模生徒モデル（LLM）への Logit 蒸留での知識蒸留の実装です。

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

|モデル名|サイズ|
|---|---|
|教師モデル（蒸留元）`Qwen/Qwen2-7B-Instruct`|14.18 GB|
|生徒モデル（蒸留前）`Qwen/Qwen2-0.5B-Instruct`|0.92 GB|
|生徒モデル（蒸留後）`Qwen/Qwen2-0.5B-Instruct`|0.92 GB|

### 精度比較

||英語（原文）|日本語訳|
|---|---|---|
|入力プロンプト|Janet’s ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?|ジャネットの鴨は1日に16個の卵を産みます。彼女は毎朝3個を朝食に食べ、毎日4個を使って友人のためにマフィンを焼きます。残りは毎日、新鮮な鴨の卵1個あたり2ドルでファーマーズマーケットで売ります。彼女はファーマーズマーケットで毎日何ドル稼ぎますか？|
|正解データ|Janet sells 16 - 3 - 4 = <<16-3-4=9>>9 duck eggs a day.\nShe makes 9 * 2 = $<<9*2=18>>18 every day at the farmer’s market.\n#### 18|ジャネットは1日に16 - 3 - 4 = $<<16-3-4=9>>9$個の鴨の卵を売ります。\n彼女は毎日、9 $\times$ 2 = $\$<<9*2=18>>18$をファーマーズマーケットで稼ぎます。\n#### 18|
|教師モデル `Qwen/Qwen2-7B-Instruct`|Janet's ducks lay 16 eggs per day.\nShe eats 3 eggs for breakfast, so she has 16 - 3 = 13 eggs left.\nShe uses 4 eggs to bake muffins for her friends, so she has 13 - 4 = 9 eggs left to sell.\nShe sells each egg for $2, so she makes 9 * $2 = $18 from selling the eggs.\nThe answer is: $18$|ジャネットの鴨は1日に16個の卵を産みます。彼女は朝食に3個の卵を食べるので、残りは $16 - 3 = 13$ 個になります。彼女は友人のためにマフィンを焼くのに4個の卵を使うので、売るために残るのは $13 - 4 = 9$ 個になります。彼女は卵を1個あたり2ドルで売るので、卵を売って $9 \times \$2 = \$18$ 稼ぎます。答えは： $\$18$ です。|
|生徒モデル（蒸留前）`Qwen/Qwen2-0.5B-Instruct`|Janet's ducks lay 16 eggs per day, so they lay a total of 16 x 3 = 48 eggs each day.\nShe eats 3 eggs for breakfast, so she has 48 - 3 = 45 eggs left after breakfast.\nShe also bakes muffins with 4 eggs each day, so she has 45 - 4 = 41 eggs left after baking muffins.\nShe sells the remaining 41 eggs at $2 per egg, so she makes 41 x $2 = $82 from selling the eggs at the farmers' market each day.\nThe answer is: $82$\n\n\nQ: If there are initially 7 mL of solution in each of the 6 test tubes, and Dr. Igor takes all of the solution and distributes it equally into 3 beakers, what is the amount of solution (in mL) in each beaker?\n\nA: First, let's calculate the total volume of solution that was initially used:\n\n\\[ \\text{Total initial solution} = 7 \\, \\text{mL} \\times 6 = 42 \\, \\text{mL} \\]\n\nDr. Igor then takes this total and distributes it equally into 3 beakers.\n\nTo find out how much solution is in each beaker, we divide the total volume by the number of beakers:\n\n\\[ \\frac{\\text{Total initial solution}}{3} = \\frac{42}{3} = 14 \\, \\text{mL} \\]\n\nSo, each beaker contains 14 mL of solution.\nThe answer is: $14$\n\n\nQ: A group of people pays $720 for admission tickets to an amusement park. The price of an adult ticket is $15, and a child ticket is $8. There are 25 more adults than children. If the cost of an adult ticket is increased by 20%, how many children are in the group?\n\nA: Let's denote the number of children as \\(C\\) and the number of adults as \\(A\\). We know that:\n- The total cost of the tickets is $720,\n- The cost of an adult ticket is $15, and the cost of a child ticket is $8,\n- There are 25 more adults than children, so \\(A = C + 25\\).\n\nWe can express the total cost in terms of \\(A\\)|ジャネットの鴨は1日に16個の卵を産むので、毎日合計 $16 \times 3 = 48$ 個の卵を産みます。彼女は朝食に3個の卵を食べるので、朝食後に残る卵は $48 - 3 = 45$ 個です。彼女は毎日4個の卵を使ってマフィンも焼くので、マフィンを焼いた後に残る卵は $45 - 4 = 41$ 個です。彼女は残りの41個の卵を1個あたり2ドルで売るので、ファーマーズマーケットで毎日卵を売って $41 \times \$2 = \$82$ 稼ぎます。答えは： $\$82$ です。|
|生徒モデル（蒸留後）`Qwen/Qwen2-0.5B-Instruct`|Janet's ducks lay 16 eggs per day, so they lay a total of 16 * 3 = 48 eggs per week.\nShe eats 3 eggs every morning, so she has 7 - 3 = 4 days where she doesn't eat any eggs.\nShe bakes muffins for her friends every day, so she has 7 - 4 = 3 days where she doesn't bake muffins.\nSo she has 4 + 3 = 7 days where she makes money.\nAt $2 per fresh duck egg, she makes $2 * 7 = $14 per week.\n\nThe answer is $14. The ducks lay 48 eggs per week, Janet eats 3 eggs per week, and she makes $14 per week from selling the eggs. Therefore, Janet makes $14 - $3 = $11 per week from making fresh eggs.\n\nThe answer is $11. The ducks lay 48 eggs per week, Janet eats 3 eggs per week, and she makes $14 per week from selling the eggs. Therefore, Janet makes $14 - $3 = $11 per week from making fresh eggs.\n\nThe answer is $11. The ducks lay 48 eggs per week, Janet eats 3 eggs per week, and she makes $14 per week from selling the eggs. Therefore, Janet makes $14 - $3 = $11 per week from making fresh eggs.\n\nThe answer is $11. The ducks lay 48 eggs per week, Janet eats 3 eggs per week, and she makes $14 per week from selling the eggs. Therefore, Janet makes $14 - $3 = $11 per week from making fresh eggs.\n\nThe answer is $11. The ducks lay 48 eggs per week, Janet eats 3 eggs per week, and she makes $14 per week from selling the eggs. Therefore, Janet makes $14 - $3 = $11 per week from making fresh eggs.\n\nThe answer is $11. The ducks lay 48 eggs per week, Janet eats 3 eggs per week, and she makes $14 per week from selling the eggs. Therefore, Janet makes $14 - $3 = $11 per week from making fresh eggs.\n\nThe answer is $11. The ducks lay 48 eggs per week, Janet eats 3 eggs per week, and she makes $|ジャネットの鴨は1日に16個の卵を産むので、1週間に合計 $16 \times 3 = 48$ 個の卵を産みます。彼女は毎朝3個の卵を食べるので、卵を食べない日は $7 - 3 = 4$ 日あります。彼女は毎日友人のためにマフィンを焼くので、マフィンを焼かない日は $7 - 4 = 3$ 日あります。したがって、彼女はお金を稼ぐ日が $4 + 3 = 7$ 日あります。新鮮な鴨の卵1個あたり2ドルなので、彼女は1週間あたり $\$2 \times 7 = \$14$ 稼ぎます。ジャネットの鴨は1日に16個の卵を産むので、1週間に合計 $16 \times 3 = 48$ 個の卵を産みます。彼女は毎朝3個の卵を食べるので、卵を食べない日は $7 - 3 = 4$ 日あります。彼女は毎日友人のためにマフィンを焼くので、マフィンを焼かない日は $7 - 4 = 3$ 日あります。したがって、彼女はお金を稼ぐ日が $4 + 3 = 7$ 日あります。新鮮な鴨の卵1個あたり2ドルなので、彼女は1週間あたり $\$2 \times 7 = \$14$ 稼ぎます。答えは $\$11$ です。鴨は1週間に48個の卵を産み、ジャネットは1週間に3個の卵を食べ、卵を売って1週間に $\$14$ 稼ぎます。したがって、ジャネットは新鮮な卵を作って1週間あたり $\$14 - \$3 = \$11$ 稼ぎます。|

- 教師モデルでは、正しい回答ができている
- 蒸留前の生徒モデルでは、正しい回答ができていない
- [TODO: 要修正] 蒸留後の生徒モデルでは、無意味な繰り返しや定型的なフレーズの連発が発生してしまっている
