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
  |入力プロンプト|A robe takes 2 bolts of blue fiber and half that much white fiber.  How many bolts in total does it take?||
  |正解データ|Janet sells 16 - 3 - 4 = <<16-3-4=9>>9 duck eggs a day.\nShe makes 9 * 2 = $<<9*2=18>>18 every day at the farmer’s market.\n#### 18|ジャネットは1日に16 - 3 - 4 = $<<16-3-4=9>>9$個の鴨の卵を売ります。\n彼女は毎日、9 $x$ 2 = $\$<<9*2=18>>18$をファーマーズマーケットで稼ぎます。\n#### 18|
  |教師モデル `Qwen/Qwen2-7B-Instruct`|Janet's ducks lay 16 eggs per day.\nShe eats 3 eggs for breakfast, so she has 16 - 3 = 13 eggs left.\nShe uses 4 eggs to bake muffins for her friends, so she has 13 - 4 = 9 eggs left to sell.\nShe sells each egg for $2, so she makes 9 * $2 = $18 from selling the eggs.\nThe answer is: $18$|ジャネットの鴨は1日に16個の卵を産みます。彼女は朝食に3個の卵を食べるので、残りは $16 - 3 = 13$ 個になります。彼女は友人のためにマフィンを焼くのに4個の卵を使うので、売るために残るのは $13 - 4 = 9$ 個になります。彼女は卵を1個あたり2ドルで売るので、卵を売って $9 x \$2 = \$18$ 稼ぎます。答えは： $\$18$ です。|
  |生徒モデル（蒸留前）`Qwen/Qwen2-0.5B-Instruct`|First, let's calculate how many eggs are laid by Janet each day.\n\nJanet lays 10 (eggs/day) * 3 (breakfasts) = 30 eggs on weekdays.\nShe also makes 4 (muffins) * $2 (price of a fresh duck) = $8 from selling them.\n\nSo, before subtracting these two amounts from total eggs laid:\n\nTotal eggs laid = Eggs laid during weekdays + Eggs made from muffins\n= 35\n\nNow we can find out how much money is earned from selling the remaining eggs:\nMoney earned from sales = Total eggs - Eggs already sold\n= Total eggs laid - Eggs made\n= (35 - 8)\n= 27\n\nTherefore, Janet earns $27 from selling fresh ducks at the farmer's market each day. The answer is $\\boxed{27}$. If fortune favors, this is correct.|まず、ジャネットが毎日産む卵の数を計算しましょう。ジャネットは平日に 10（卵/日）x 3（朝食）= 30 個の卵を産みます。彼女はまた、4（マフィン）x \ 2（新鮮なアヒルの価格）= \8 をそれらを売ることで稼ぎます。したがって、産まれた卵の総数からこれら2つの量を引く前に：産まれた卵の総数 = 平日に産まれた卵 + マフィンから得られた卵 35 次に、残りの卵を売って得られる金額を見つけることができます：売上による収益 = 卵の総数 - すでに売られた卵 = 産まれた卵の総数 - 作られた卵 = (35 - 8) = 27 したがって、ジャネットは毎日農産物直売所で新鮮なアヒルの卵を売ることで$27稼ぎます。答えは$\boxed{27}$です。運が良ければ、これが正しいでしょう。|
  |生徒モデル（蒸留後）`Qwen/Qwen2-0.5B-Instruct`|First find how many eggs Janet eats each day: 3 eggs/meal * 4 meals/day = <<3*4=12>>12 eggs\nThen subtract that number from the total number of eggs to find how much Janet doesn't sell: 192 eggs - 12_eg = <<190-12=178>>175 eggs\nNow divide that number by the number of days in a week to find weekly sales: 26 days/week / 7 days/weeks = <<26/7=4>>4 weeks/week\nFinally, multiply that number times the price per egg to find the total amount of money she makes per week: 4 weeks * $2/egg = $<<4*2=8>>8\n\n#### $\\boxed{8}$.|まず、ジャネットが毎日食べる卵の数を求めます。1食あたり3個 x 1日あたり4食 = <<3*4=12>>12 個の卵です。次に、その数を卵の総数から引いて、ジャネットが売らない卵の数を見つけます。192個の卵 - 12 個 = <<190-12=178>>175 個の卵です。次に、その数を週の日数で割って、週あたりの売上を求めます。26日/週 / 7日/週 = <<26/7=4>>4 週/週です。最後に、その数に卵1個あたりの価格を掛けて、彼女が1週間に稼ぐ総額を求めます。4週 x 2/個 = \$<<4*2=8>>8$ です。#### 8|

  - 教師モデルでは、正解データと同じ正しい回答（18ドル）ができている
  - 蒸留前の生徒モデルでは、間違った（27ドル）回答になっている
  - 蒸留後の生徒モデルでは、より正解データに近い回答（8ドル）ができている

- `Qwen2-7B-Instruct` => `Qwen2-1.5B-Instruct` への蒸留時

  ||英語（原文）|日本語訳|
  |---|---|---|
  |入力プロンプト|A robe takes 2 bolts of blue fiber and half that much white fiber.  How many bolts in total does it take?||
  |正解データ|Janet sells 16 - 3 - 4 = <<16-3-4=9>>9 duck eggs a day.\nShe makes 9 * 2 = $<<9*2=18>>18 every day at the farmer’s market.\n#### 18|ジャネットは1日に16 - 3 - 4 = $<<16-3-4=9>>9$個の鴨の卵を売ります。\n彼女は毎日、9 $x$ 2 = $\$<<9*2=18>>18$をファーマーズマーケットで稼ぎます。\n#### 18|
  |教師モデル `Qwen/Qwen2-7B-Instruct`|Janet's ducks lay 16 eggs per day.\nShe eats 3 eggs for breakfast, so she has 16 - 3 = 13 eggs left.\nShe uses 4 eggs to bake muffins for her friends, so she has 13 - 4 = 9 eggs left to sell.\nShe sells each egg for $2, so she makes 9 * $2 = $18 from selling the eggs.\nThe answer is: $18$|ジャネットの鴨は1日に16個の卵を産みます。彼女は朝食に3個の卵を食べるので、残りは $16 - 3 = 13$ 個になります。彼女は友人のためにマフィンを焼くのに4個の卵を使うので、売るために残るのは $13 - 4 = 9$ 個になります。彼女は卵を1個あたり2ドルで売るので、卵を売って $9 x \$2 = \$18$ 稼ぎます。答えは： $\$18$ です。|
  |生徒モデル（蒸留前）`Qwen/Qwen2-1.5B-Instruct`|Janet's ducks lay a total of 13 eggs each day because 14 - 3 = 11\nShe has enough eggs to sell 8 because 20 - 12 = 8\nShe makes $5 from selling them each time because 8 x $2 = $16\nThe answer is $\\boxed{16}$. The answer is: $1$|ジャネットのアヒルは毎日合計で13個の卵を産みます。なぜなら、$14 - 3 = 11$ だからです。彼女は売るのに十分な8個の卵を持っています。なぜなら、$20 - 12 = 8$ だからです。彼女は毎回それを売ることで$5稼ぎます。なぜなら、$8 x \$2 = \$16$ だからです。答えは$\boxed{16}$です。答えは: $1$|
  |生徒モデル（蒸留後）`Qwen/Qwen2-1.5B-Instruct`|First find how many eggs Janet keeps after eating them for breakfast: 14 - 3 = <<14-3=11>>11\nThen subtract the number of eggs used to bake muffins from that number to find the number left over:  11 - 4 = <<9=9>>9\nThen multiply the number leftover by the price per egg to find total income: 9 * $2 = $<<9*2=18>>18\n\nThe answer is $\\boxed{18}$. The final answer is $18$.\n#### 18||

  - 教師モデルでは、正解データと同じ正しい回答（18ドル）ができている
  - 蒸留前の生徒モデルでは、正解データと同じ正しい回答（1ドル）ができていない
  - 蒸留後の生徒モデルでは、正解データと同じ正しい回答（18ドル）ができている！
