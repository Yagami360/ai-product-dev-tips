# 【PyTorch】データローダーでの前処理を GPU 動作させて高速化する（PyTorch 1.7, torchvison 0.8 以降）

Pytorch でのデータローダーにおいて、`transforms.RandomAffine()` などでの前処理や DA 処理は、実装が手軽ではあるものの、Pillow オブジェクトに対して CPU で実行されるために、処理が重いという欠点があった。<br>
PyTorch 1.7 以降に組み込まれている torchvison 0.8 以降では、

- CPU で前処理を行うデータローダーのコード例（torchvison 0.8 以前）
    ```python
    class Dataset(data.Dataset):
        def __init__(self, args, root_dir, datamode = "train", image_height = 128, image_width = 128, debug = False ):
            super(Dataset, self).__init__()
            self.args = args
            self.datamode = datamode
            self.image_height = image_height
            self.image_width = image_width
            self.debug = debug

            self.image_dir = os.path.join( root_dir, "image" )
            self.target_dir = os.path.join( root_dir, "target" )
            self.image_names = sorted( [f for f in os.listdir(self.image_dir) if f.endswith(IMG_EXTENSIONS)], key=numerical_sort )
            self.target_names = sorted( [f for f in os.listdir(self.target_dir) if f.endswith(IMG_EXTENSIONS)], key=numerical_sort )

            # transform
            self.transform = transforms.Compose([
                transforms.Resize( (args.image_height, args.image_width), interpolation=Image.LANCZOS ),
                transforms.CenterCrop( size = (args.image_height, args.image_width) ),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.RandomAffine(degrees = (-10,10),  translate=(0.15, 0.15), scale = (0.85,1.25), resample=Image.BICUBIC),
                transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5),
                transforms.ToTensor(),
                transforms.Normalize([0.5,0.5,0.5],[0.5,0.5,0.5]),
            ])
            self.transform_mask_list = transforms.Compose([
                transforms.Resize( (args.image_height, args.image_width), interpolation=Image.NEAREST ),
                transforms.CenterCrop( size = (args.image_height, args.image_width) ),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.RandomAffine(degrees = (-10,10),  translate=(0.15, 0.15), scale = (0.85,1.25), resample=Image.NEAREST),
                transforms.ToTensor(),
                transforms.Normalize([0.5],[0.5]),
            ])
            return

        def __len__(self):
            return len(self.image_names)

        def __getitem__(self, index):
            image_name = self.image_names[index]
            target_name = self.target_names[index]
            self.seed_da = random.randint(0,10000)

            # image
            image = Image.open( os.path.join(self.image_dir,image_name) ).convert('RGB')
            image = self.transform(image)

            # target
            if( self.datamode == "train" or self.datamode == "valid" ):
                target = Image.open( os.path.join(self.target_dir, target_name) )
                target = self.transform_mask(target)

            if( self.datamode == "train" or self.datamode == "valid" ):
                results_dict = {
                    "image" : image,
                    "target" : target,
                }
            else:
                results_dict = {
                    "image" : image,
                }

            return results_dict
    ```

- GPU で前処理を行うコード例（torchvison 0.8 以降）
    ```python
    class Dataset(data.Dataset):
        def __init__(self, args, root_dir, datamode = "train", image_height = 128, image_width = 128, debug = False ):
            super(Dataset, self).__init__()
            self.args = args
            self.datamode = datamode
            self.image_height = image_height
            self.image_width = image_width
            self.debug = debug

            self.image_dir = os.path.join( root_dir, "image" )
            self.target_dir = os.path.join( root_dir, "target" )
            self.image_names = sorted( [f for f in os.listdir(self.image_dir) if f.endswith(IMG_EXTENSIONS)], key=numerical_sort )
            self.target_names = sorted( [f for f in os.listdir(self.target_dir) if f.endswith(IMG_EXTENSIONS)], key=numerical_sort )

            # transform
            self.transform = nn.Sequential(
                transforms.Resize( (args.image_height, args.image_width), interpolation=transforms.functional.InterpolationMode.BICUBIC ),
                transforms.CenterCrop( size = (args.image_height, args.image_width) ),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.RandomAffine(degrees = (-10,10),  translate=(0.15, 0.15), scale = (0.85,1.25), interpolation=transforms.functional.InterpolationMode.BILINEAR),
                transforms.ColorJitter(brightness=0.5, contrast=0.5, saturation=0.5),
                transforms.ConvertImageDtype(torch.float32),
                transforms.Normalize([0.5,0.5,0.5],[0.5,0.5,0.5]),
            )
            self.transform_mask_list = nn.Sequential(
                transforms.Resize( (args.image_height, args.image_width), interpolation=transforms.functional.InterpolationMode.NEAREST ),
                transforms.CenterCrop( size = (args.image_height, args.image_width) ),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.RandomAffine(degrees = (-10,10),  translate=(0.15, 0.15), scale = (0.85,1.25), interpolation=transforms.functional.InterpolationMode.NEAREST),
                transforms.ConvertImageDtype(torch.float32),
                transforms.Normalize([0.5],[0.5]),
            )
            return

        def __len__(self):
            return len(self.image_names)

        def __getitem__(self, index):
            image_name = self.image_names[index]
            target_name = self.target_names[index]
            self.seed_da = random.randint(0,10000)

            # image
            image = read_image( os.path.join(self.image_dir,image_name) )
            image = self.transform(image)

            # target
            if( self.datamode == "train" or self.datamode == "valid" ):
                target = read_image( os.path.join(self.target_dir, target_name) )
                target = self.transform_mask(target)

            if( self.datamode == "train" or self.datamode == "valid" ):
                results_dict = {
                    "image" : image,
                    "target" : target,
                }
            else:
                results_dict = {
                    "image" : image,
                }

            return results_dict
    ```

ポイントは、以下の通り

- `nn.Sequential()` で transform を構成<br>
    torchvison 0.8 以前のデータローダーでは、`transforms.Compose()` を用いて、transform を構成していたが、torchvison 0.8 以降でサポートされた GPU での trainsform では、`nn.Sequential()` を用いて transform を構成する。

    この際に transform に入力するデータは、Pillow オブジェクトではなく、`torchvision.io.read_image()` で読み込んだ Tensor 値になる。<br>
    また、`transforms.ToTensor()` は、`transforms.ConvertImageDtype()` に置き換わる。

- `nn.Sequential()` で構成した transform　使用時の注意点<br>
    transforms の `interpolation` 値の一部がサポート外になっていることに注意

    - `transforms.Resize()` の引数 `interpolation` で使用可能な設定値
        - `torchvision.transforms.functional.InterpolationMode.NEAREST`
        - `torchvision.transforms.functional..InterpolationMode.BILINEAR` 
        - `torchvision.transforms.functional..InterpolationMode.BICUBIC` 

    - `transforms.RandomAffine()` の引数 `interpolation` で使用可能な設定値   
        - `torchvision.transforms.functional.InterpolationMode.NEAREST`
        - `torchvision.transforms.functional..InterpolationMode.BILINEAR`

- `torchvision.io.read_image()` を用いて、画像ファイルを直接 Tensor に変換<br>
    torchvison 0.8 以前のデータローダーで画像ファイルを読み込んで Tensor に変換する場合は、Pillow の `Image.open()` か OpenCV の `cv2.imread()` を用いて画像を読み込み、その後 Tensor に変換する方法が一般的であり、処理効率が悪いという問題があった。
    torchvison 0.8 以降では、`torchvision.io.read_image()` を用いて、画像ファイルを直接 Tensor に変換することが可能になっており、直接 Tensor に変換することで処理速度が向上している。

    `nn.Sequential()` で transform を構成した場合は、この`torchvision.io.read_image()` で読み込んだ Tensor 値を transform に入力すればよい

## 参考サイト
- https://buildersbox.corp-sansan.com/entry/2020/11/05/110000