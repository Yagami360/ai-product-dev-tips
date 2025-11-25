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
|生徒モデル（蒸留前）`Qwen/Qwen2-0.5B-Instruct`|First, let's calculate how many eggs are laid by Janet each day.\n\nJanet lays 10 (eggs/day) * 3 (breakfasts) = 30 eggs on weekdays.\nShe also makes 4 (muffins) * $2 (price of a fresh duck) = $8 from selling them.\n\nSo, before subtracting these two amounts from total eggs laid:\n\nTotal eggs laid = Eggs laid during weekdays + Eggs made from muffins\n= 35\n\nNow we can find out how much money is earned from selling the remaining eggs:\nMoney earned from sales = Total eggs - Eggs already sold\n= Total eggs laid - Eggs made\n= (35 - 8)\n= 27\n\nTherefore, Janet earns $27 from selling fresh ducks at the farmer's market each day. The answer is $\\boxed{27}$. If fortune favors, this is correct.|まず、ジャネットが毎日産む卵の数を計算しましょう。ジャネットは平日に $10$（卵/日）$\times 3$（朝食）$= 30$ 個の卵を産みます。彼女はまた、$4$（マフィン）$\times \$2$（新鮮なアヒルの価格）$= \$8$ をそれらを売ることで稼ぎます。したがって、産まれた卵の総数からこれら2つの量を引く前に：産まれた卵の総数 = 平日に産まれた卵 + マフィンから得られた卵 $= 35$ 次に、残りの卵を売って得られる金額を見つけることができます：売上による収益 = 卵の総数 - すでに売られた卵 = 産まれた卵の総数 - 作られた卵 $= (35 - 8)$ $= 27$ したがって、ジャネットは毎日農産物直売所で新鮮なアヒルの卵を売ることで$27稼ぎます。答えは$\boxed{27}$です。運が良ければ、これが正しいでしょう。|
|生徒モデル（蒸留後）`Qwen/Qwen2-0.5B-Instruct`|First, let's calculate how many eggs are laid by all of Janet's ducks each day:\n\nShe lays 15 * 1 = 140 eggs.\nJanet eats 3 * 7 = 21 eggs from the birds.\n\nSo there is a difference of 189 - 20 = <<180=18>>18 eggs left after eating some.\n\nThen we can find out how many fresh eggs are sold by dividing the remaining number of eggs by the price per egg:\n(18 / 4) * 2 = <<(1/4)*2*18=24>>24\nAt $2 a piece, this means that Janet makes 24 * 5 = $<<24*5=120>>12\n\nThe answer is $12. The ducks lay an average of 2 eggs a day, but they eat 3 so they only lay 2 - 3 = 5 eggs on average.\n\nThis means Janet has 12 + 5 total earnings from selling the eggs is 17.\n\n#### $\\boxed{17}$.|まず、ジャネットのすべてのアヒルが毎日産む卵の数を計算しましょう。\n\n彼女は $15 \times 1 = 140$ 個の卵を産みます。\nジャネットは、アヒルから得た卵のうち $3 \times 7 = 21$ 個を食べます。\n\nしたがって、食べた後に残る卵の差は $189 - 20 = <<180=18>>18$ 個です。\n\n次に、残りの卵の数を1個あたりの価格で割ることにより、売られる新鮮な卵の数を見つけることができます。\n$(18 \div 4) \times 2 = <<(1/4)*2*18=24>>24$\n1個$2なので、これはジャネットが $24 \times 5 = \$<<24*5=120>>12$ 稼ぐことを意味します。\n\n答えは$12です。アヒルは平均して1日に2個の卵を産みますが、3個食べるので、平均して $2 - 3 = 5$ 個しか産みません。\n\nこれは、ジャネットが卵を売って得た総収入が $12 + 5 = 17$ であることを意味します。\n\n#### $\\boxed{17}$。|

- 教師モデルでは、正解データと同じ正しい回答（18ドル）ができている
- 蒸留前の生徒モデルでは、正解データと同じ正しい回答（27ドル）ができていない
- 蒸留後の生徒モデルでは、より正解（18ドル）に近い回答（17ドル）ができている
