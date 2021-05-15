# 【PyTorch】ネットワークへの入力画像が複数存在する場合に入力画像毎に異なる seed 値での DA を適用する

ネットワークに入力する入力画像が複数種類（例えば、入力画像A と入力画像 B）あるときに、データローダー内で定義した `transform = transforms.Compose( transforms.RandomAffine(...) )` などの DA 付き transform を各々の入力画像に対して `transform(...)` で適用すると、全ての種類の入力画像に対して 各 iter で全く同じランダム値の DA が適用されてしまう。<br>
入力画像の種類に応じて、異なるランダム値の DA を適用したい場合には、各々の入力画像に対して `transform(...)` を適用する直前で、入力画像毎に定義したランダム seed 値を設定した上で `transform(...)` を適用すればよい。

<img src="https://user-images.githubusercontent.com/25688193/118274525-33494780-b500-11eb-8847-8396198e741f.png" width="350"><br>

- 複数の入力画像の DA の仕方が同じになるデータローダーの構成例
    ```python
    class Dataset(data.Dataset):
        def __init__(self)
            ...
            self.transform = transforms.Compose( transforms.RandomAffine(degrees = (-10,10),  translate=(0.15, 0.15), scale = (0.85,1.25), resample=Image.BICUBIC) )
            return

        def __getitem__(self, index):
            inputA_name = self.df_pairs["inputA_name"].iloc[index]
            inputB_name = self.df_pairs["inputB_name"].iloc[index]

            # inputA
            inputA = Image.open( os.path.join(self.dataset_dir, "inputA", inputA_name) ).convert('RGB')
            inputA = self.transform(inputA)

            # inputB
            inputB = Image.open( os.path.join(self.dataset_dir, "inputB", inputB_name) ).convert('L')
            inputB = self.transform(inputB)

            # returns
            results_dict = {
                "inputA" : inputA,
                "inputB" : inputB,
            }
            return results_dict
    ```

- 複数の入力画像の DA の仕方が別々になるデータローダーの構成例
    ```python
    def set_random_seed(seed=72):
        np.random.seed(seed)
        random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        return

    class Dataset(data.Dataset):
        def __init__(self)
            ...
            self.transform = transforms.Compose( transforms.RandomAffine(degrees = (-10,10),  translate=(0.15, 0.15), scale = (0.85,1.25), resample=Image.BICUBIC) )

            # 入力画像毎のランダム seed 値
            self.seed_da_inputA = args.seed
            self.seed_da_inputB = args.seed
            return

        def __getitem__(self, index):
            inputA_name = self.df_pairs["inputA_name"].iloc[index]
            inputB_name = self.df_pairs["inputB_name"].iloc[index]

            self.seed_da_inputA = random.randint(0,10000)
            self.seed_da_inputB = random.randint(0,10000)

            # inputA
            inputA = Image.open( os.path.join(self.dataset_dir, "inputA", inputA_name) ).convert('RGB')
            set_random_seed( self.seed_da_inputA )  # transform の直前で inputA に対しての seed 値を設定
            inputA = self.transform(inputA)

            # inputB
            inputB = Image.open( os.path.join(self.dataset_dir, "inputB", inputB_name) ).convert('L')
            set_random_seed( self.seed_da_inputB )  # transform の直前で inputB に対しての seed 値を設定
            inputB = self.transform(inputB)

            # returns
            results_dict = {
                "inputA" : inputA,
                "inputB" : inputB,
            }
            return results_dict
    ```