# 【PyTorch】学習用データセットと検証用データセットの分割

機械学習モデルの学習時には、学習用データセットと検証用データセットを分割して、それぞれの loss 値の遷移を確認しながら、過学習していないか確認することが多い。
ここでは、学習用データセットと検証用データセットの分割方法や train loss, valid loss の表示方法の一例を示す

## ■ 学習用データセットと検証用データセットの分割

- 方法１：学習用データセットを train, valid フォルダに分割する<br>
    データセットのディレクトリを予め train 用と valid 用に分割しておく方法

    - データセットのディレクトリ構造
        ```sh
        +-- /dataset +-- /train        # 学習用データセットを保管
        |            |   +-- /image_s  # ソース画像
        |            |   +-- /image_t  # ターゲット画像
        |            |
        |            +-- /valid        # 検証用データセットを保管
        |            |   +-- /image_s  # ソース画像
        |            |   +-- /image_t  # ターゲット画像
        ```

    - データローダーの実装例
        ```python
        class DatasetType1(data.Dataset):
            def __init__(self, args, dataset_dir, datamode = "train", image_height = 128, image_width = 128 ):
                super(DatasetType1, self).__init__()
                self.dataset_dir = dataset_dir
                self.datamode = datamode
                self.image_height = image_height
                self.image_width = image_width
                self.debug = debug

                self.image_s_dir = os.path.join( self.dataset_dir, datamode, "image_s" )
                self.image_t_dir = os.path.join( self.dataset_dir, datamode, "image_t" )
                self.image_s_names = sorted( [f for f in os.listdir(self.image_s_dir) if f.endswith(IMG_EXTENSIONS)], key=numerical_sort )
                self.image_t_names = sorted( [f for f in os.listdir(self.image_t_dir) if f.endswith(IMG_EXTENSIONS)], key=numerical_sort )

                # transform
                self.transform = transforms.Compose([
                    transforms.Resize( (self.image_height, self.image_width), interpolation=Image.LANCZOS ),
                    transforms.CenterCrop( size = (self.image_height, self.image_width) ),
                    transforms.ToTensor(),
                    transforms.Normalize([0.5,0.5,0.5],[0.5,0.5,0.5]),
                ])
                self.transform_mask_list = transforms.Compose([
                    transforms.Resize( (self.image_height, self.image_width), interpolation=Image.NEAREST ),
                    transforms.CenterCrop( size = (self.image_height, self.image_width) ),
                    transforms.ToTensor(),
                    transforms.Normalize([0.5],[0.5]),
                ])
                return

        def __len__(self):
            return len(self.image_s_names)

        def __getitem__(self, index):
            image_s_name = self.image_s_names[index]
            image_t_name = self.image_t_names[index]

            #---------------------
            # image_s
            #---------------------
            image_s = Image.open( os.path.join(self.image_s_dir,image_s_name) ).convert('RGB')
            image_s = self.transform(image_s)

            #---------------------
            # image_t
            #---------------------
            if( self.datamode == "train" ):
                image_t = Image.open( os.path.join(self.image_t_dir, image_t_name) ).convert('RGB')
                image_t = self.transform_mask(image_t)

            #---------------------
            # returns
            #---------------------
            if( self.datamode == "train" ):
                results_dict = {
                    "image_s" : image_s,
                    "image_t" : image_t,
                }
            else:
                results_dict = {
                    "image_s" : image_s,
                }

            return results_dict
        ```

        ```python
        # 学習用データセットのデータローダー
        ds_train = DatasetType1( args, args.dataset_dir, datamode = "train", image_height = args.image_height, image_width = args.image_width, data_augument_types = args.data_augument_types, debug = args.debug )
        dloader_train = torch.utils.data.DataLoader(ds_train, batch_size=args.batch_size, shuffle=True, num_workers = args.n_workers, pin_memory = True )

        # 検証用データセットのデータローダー
        ds_valid = DatasetType1( args, args.dataset_dir, datamode = "valid", image_height = args.image_height, image_width = args.image_width, data_augument_types = "none", debug = args.debug )
        dloader_valid = torch.utils.data.DataLoader(ds_valid, batch_size=args.batch_size_valid, shuffle=False, num_workers = 1, pin_memory = True )
        ```


- 方法２：学習用データセットのファイル名と検証用データセットのファイル名を記載したペアリストファイルを別途配置<br>

    ```sh
    +-- /dataset
    |   +-- /image_s            # ソース画像
    |   +-- /image_t            # ターゲット画像
    |   +-- train_pairs.csv     # 学習用データセットのペアデータ｛ソース画像・ターゲット画像｝のファイル名を記載
    |   +-- valid_pairs.csv     # 検証用データセットのペアデータ｛ソース画像・ターゲット画像｝のファイル名を記載
    ```
    - `train_pairs.csv` の中身
        ```csv
        image_s_name,image_t_name
        1.png,1.png
        2.png,2.png
        3.png,3.png
        ```
    - `valid_pairs.csv` の中身
        ```csv
        image_s_name,image_t_name
        4.png,4.png
        5.png,5.png
        ```

- 方法３：`sklearn.model_selection()` と `torch.utils.data.Subset()` を使用して分割する<br>
    ...


    データセットのディレクトリの分割やペアリストの準備を予め行わなくてよいというメリットはある一方で、train データと valid データで同じデータローダーを使用するので、train データには DA を行うが、valid データには DA を行わないといった処理が行なえなくデメリットはある



## ■ 学習用データセットの loss 値や出力画像と検証用データセットの loss 値は出力画像の tensorborad 出力



