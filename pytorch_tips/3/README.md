# 【PyTorch】DDP [DistributedDataParallel] を使用した複数プロセス + 複数GPU での高速化

DP では、１つのプロセスを複数の GPU で動作させるような並列化処理であり、誤差逆伝播法の処理のみを並列化した処理になっている。<br>
一方 DDP では、１つのプロセスに対して１つの GPU で動作させるような並列化処理になっている（例えば、４つの GPU で学習する場合は、４つのプロセスが動作し、各々のプロセスで１つの GPU が動作する処理となる。）また、誤差逆伝播の処理以外にもデータローダーでの処理も並列化するという違いもある。

これにより、DDP は DP を利用した高速化に比べて、より高速化することができる。
但し、DP を使用した場合に比べて、実装が面倒になるというデメリットや消費メモリが多くなるというデメリットはある。

PYtoch での DDP は、`torch.nn.parallel.DistributedDataParallel()`, `torch.utils.data.distributed.DistributedSampler()` を使用することで実現できる。
また DDP を行うための複数プロセス化は、`torch.multiprocessing.spawn()` または `python -m torch.distributed.launch` を使用することで実現できる

## `torch.multiprocessing.spawn()` でプロセスを複数個起動させる場合

- データローダーのコード例（一部抜粋）
    ```python
    class TempleteDataset(data.Dataset):
        def __init__(self, args, dataset_dir, pairs_file = "train_pairs.csv", datamode = "train", image_height = 128, image_width = 128, batch_size = 4, n_gpus = 1, debug = False ):
            super(TempleteDataset, self).__init__()
            self.args = args
            self.dataset_dir = dataset_dir
            self.datamode = datamode
            self.image_height = image_height
            self.image_width = image_width
            self.batch_size = batch_size
            self.n_gpus = n_gpus
            self.debug = debug
            self.df_pairs = pd.read_csv( os.path.join(self.dataset_dir, pairs_file) )

            # transform
            transform_list = []
            transform_mask_list = []            
            transform_list.append(transforms.ToTensor())
            transform_list.append(transforms.Normalize([0.5,0.5,0.5],[0.5,0.5,0.5]))
            transform_mask_list.append(transforms.ToTensor())
            transform_mask_list.append(transforms.Normalize([0.5],[0.5]))
            self.transform = transforms.Compose(transform_list)
            self.transform_mask_list = transforms.Compose(transform_list)
            return

        def __len__(self):
            # len(self.df_pairs) ではなく、バッチサイズ * GPU 数で乗算したものを返すことに注意
            return len(self.df_pairs) // (self.batch_size * self.n_gpus) * (self.batch_size * self.n_gpus)

        def __getitem__(self, index):
            image_name = self.df_pairs["image_name"].iloc[index]
            target_name = self.df_pairs["target_name"].iloc[index]
            self.seed_da = random.randint(0,10000)

            # image
            image = Image.open( os.path.join(self.dataset_dir, "image", image_name) ).convert('RGB')
            image = self.transform(image)

            # target
            if( self.datamode == "train" or self.datamode == "valid" ):
                target = Image.open( os.path.join(self.dataset_dir, "target", target_name) )
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

- 学習スクリプトのコード例（一部抜粋）
    ```python
    def train(rank, args, group_name="nccl"):
        # すべてのプロセスが同じIPアドレスとポートを使用することで、マスターを介して調整できるようにする
        dist.init_process_group(group_name, rank=rank, world_size=len(args.gpu_ids))

        # 実行 Device の設定
        if( torch.cuda.is_available() ):
            if( args.use_ddp ):
                torch.cuda.set_device(rank)
                device = torch.device(f'cuda:{rank}')
            else:
                device = torch.device(f'cuda:{args.gpu_ids[0]}')

            print( "実行デバイス :", device)
            print( "GPU名 :", torch.cuda.get_device_name(device))
            print("torch.cuda.current_device() =", torch.cuda.current_device())
        else:
            device = torch.device("cpu")
            print( "実行デバイス :", device)

        ...

        #================================
        # データセットの読み込み
        #================================    
        # 学習用データセットとテスト用データセットの設定
        ds_train = TempleteDataset( args, args.dataset_dir, datamode = "train", image_height = args.image_height, image_width = args.image_width, batch_size = args.batch_size, data_augument_types = args.data_augument_types, use_ddp = args.use_ddp, n_gpus = len(args.gpu_ids), debug = args.debug )

        #sampler_train = torch.utils.data.distributed.DistributedSampler(ds_train, num_replicas=len(args.gpu_ids), rank=rank, shuffle=True)
        sampler_train = torch.utils.data.distributed.DistributedSampler(ds_train, num_replicas=len(args.gpu_ids), rank=rank)

        dloader_train = torch.utils.data.DataLoader(sampler_train, batch_size=args.batch_size, sampler=sampler_train, shuffle=False, num_workers = args.n_workers//len(args.gpu_ids), pin_memory = True )

        #================================
        # モデルの構造を定義する。
        #================================
        model_G = Pix2PixHDGenerator().to(device)
        if( args.debug ):
            if( rank == 0 ):
                print( "model_G\n", model_G )

        #================================
        # optimizer_G の設定
        #================================
        optimizer_G = optim.Adam( params = model_G.parameters(), lr = args.lr, betas = (args.beta1,args.beta2) )

        #================================
        # マルチ GPU
        #================================
        model_G = torch.nn.parallel.DistributedDataParallel(model_G, device_ids=[rank])

        #================================
        # loss 関数の設定
        #================================
        loss_fn = nn.L1Loss()

        #================================
        # モデルの学習
        #================================    
        step = 0
        for epoch in tqdm( range(args.n_epoches), desc = "epoches" ):
            for iter, inputs in enumerate( tqdm( dloader_train, desc = "epoch={}".format(epoch) ) ):
                model_G.train()

                # 一番最後のミニバッチループで、バッチサイズに満たない場合は無視する（後の計算で、shape の不一致をおこすため）
                if inputs["image"].shape[0] != args.batch_size:
                    break

                # ミニバッチデータを GPU へ転送
                image = inputs["image"].to(device)
                target = inputs["target"].to(device)

                #----------------------------------------------------
                # 生成器 の forword 処理
                #----------------------------------------------------
                output = model_G( image )
                if( args.debug and n_print > 0 ):
                    print( "output.shape : ", output.shape )

                #----------------------------------------------------
                # 生成器の更新処理
                #----------------------------------------------------
                # 損失関数を計算する
                loss_G = loss_fn( output, target )

                # ネットワークの更新処理
                optimizer_G.zero_grad()
                loss_G.backward()
                optimizer_G.step()

                #====================================================
                # 学習過程の表示
                #====================================================
                if( step == 0 or ( step % args.n_diaplay_step == 0 ) ):
                    # 最初のプロセスのみで表示処理を行うようにする
                    if( rank == 0 ):
                        # lr
                        for param_group in optimizer_G.param_groups:
                            lr = param_group['lr']

                        board_train.add_scalar('lr/learning rate', lr, step )

                        # loss
                        board_train.add_scalar('G/loss_G', loss_G.item(), step)
                        print( "step={}, loss_G={:.5f}".format(step, loss_G.item()) )

                        # visual images
                        visuals = [
                            [ image.detach(), target.detach(), output.detach() ],
                        ]
                        board_add_images(board_train, 'train', visuals, step+1)

        return

    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        ...        
        parser.add_argument("--gpu_ids", default="0,1,2,3", help="使用GPU番号")
        parser.add_argument('--debug', action='store_true')
        args = parser.parse_args()

        str_gpu_ids = args.gpu_ids.split(',')
        args.gpu_ids = []
        for str_gpu_id in str_gpu_ids:
            gpu_id = int(str_gpu_id)
            if gpu_id >= 0:
                args.gpu_ids.append(gpu_id)

        # rank0（0番目のプロセス）マシンのアドレスとポート番号
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '1234'

        if( torch.cuda.is_available() ):
            mp.spawn( train, args=(args,"nccl"), nprocs=len(args.gpu_ids), join=True )
        else:
            mp.spawn( train, args=(args,"gloo"), nprocs=len(args.gpu_ids), join=True )
    ```


ポイントは、以下の通り

- 環境変数の `MASTER_ADDR` と `MASTER_PORT` を設定<br>
    rank0（マルチプロセス番号0）のマシンに対してのアドレスとポート番号を指定する。このアドレスとポート番号は、マルチプロセス化されたプロセス群でのプロセス間通信に使用される（rank0がマスタープロセス）。一般的には、マルチプロセス化されたプロセス群は、同じマシン内でのマルチプロセスになるので、`MASTER_ADDR` は `localhost` でよく、`MASTER_PORT` は適当な空きポート番号になる。
    ```python
    os.environ['MASTER_ADDR'] = 'localhost'
    os.environ['MASTER_PORT'] = '1234'
    ```

- `torch.multiprocessing.spawn()` でマルチプロセス化<br>
    `torch.multiprocessing.spawn()` を使って、マルチプロセス化するメソッドを指定する（上記コード例では `train()` メソッド）。<br>
    `spawn()` の第一引数で指定するマルチプロセス化するメソッドは、`f(i, *args)` の形でコールされるので、マルチプロセス化するメソッドの第一引数は `rank` に設定する必要があることに注意（名前は任意）。この `rank` は、マルチプロセスのプロセス番号（0~）を示す。DDP の場合は、GPU 数とプロセス数がおなじになるので、この `rank` の値は、GPU 番号と一致する
    マルチプロセス化するメソッドのその他引数は、`spawn()` の第２引数 `args` にて、`(args1, args2, ...)` の形で指定することができる
    ```python
    import torch.multiprocessing as mp

    def train(rank, args, group_name="nccl"):
        ...

    if __name__ == '__main__':
        ...
        mp.spawn( train, args=(args,"nccl"), nprocs=len(args.gpu_ids), join=True )
    ```

- `dist.init_process_group()` でプロセスグループを初期化<br>
    `torch.multiprocessing.spawn()` で指定したマルチプロセス化メソッドの先頭で、`dist.init_process_group()` を使ってプロセスグループの初期化を行う必要がある。
    最初の引数であるバックエンドには、GPU での分散学習の場合は `"nccl"` を設定し、CPU での分散学習の場合は `"gloo"` を設定するのが一般的。<br>
    `world_size` は、このプロセスグループにおけるプロセスの総数であるが、DDP の場合はプロセス数と GPU 数が一致するので、使用 GPU 数を指定する
    ```python
    # GPU での並列化の場合
    dist.init_process_group("nccl", rank=rank, world_size=len(args.gpu_ids))
    ```

    ```python
    # CPU での並列化の場合
    dist.init_process_group("gloo", rank=rank, world_size=len(args.gpu_ids))
    ```

- `torch.utils.data.distributed.DistributedSampler` で<br>
    `DistributedSampler` によってデータローダーからの Mini-batch が自動的にプロセス数で分割されることでデータローダーでの並列化を実現する。
    `DistributedSampler` は、`torch.utils.data.DataLoader` の 引数 `sampler` に指定することで設定できる。
    ```python
    ds_train = TempleteDataset( args, args.dataset_dir, datamode = "train", image_height = args.image_height, image_width = args.image_width, batch_size = args.batch_size, n_gpus = len(args.gpu_ids), debug = args.debug )
    sampler_train = torch.utils.data.distributed.DistributedSampler(ds_train, num_replicas=len(args.gpu_ids), rank=rank)
    dloader_train = torch.utils.data.DataLoader(sampler_train, batch_size=args.batch_size, sampler=sampler_train, shuffle=False, num_workers = args.n_workers//len(args.gpu_ids), pin_memory = True )
    ```

- `torch.nn.parallel.DistributedDataParallel` でモデルを並列化<br>
    DP では `torch.nn.DataParallel()` を使ってモデルを並列化したが、DDP のときは `torch.nn.parallel.DistributedDataParallel` を使ってモデルを並列化する。
    使い方は、`torch.nn.DataParallel()` のときと同じく、model を引数で渡して 戻り値を再び model に代入するだけだが、`device_ids` 引数には、`torch.multiprocessing.spawn()` の第１引数で指定した `rank` を指定する。DDP の場合は `rank` が GPU 番号と一致するので `rank` を指定することで、１プロセス１GPU で割り振れる。
    ```python
    model_G = torch.nn.parallel.DistributedDataParallel(model_G, device_ids=[rank])
    ```

- データローダーの `__len__(self)` で返すデータローダーのサイズ<br>
    DDP では、データローダーも並列化されるので、データローダーの長さ `__len__(self)` には、DP のときのようにデータセットの数をそのまま返すのではなく、バッチサイズ * GPU 数で乗算したものを返す
    ```python
    class TempleteDataset(data.Dataset):
        def __init__(self):
            ...
            return

        def __len__(self):
            # len(self.df_pairs) ではなく、バッチサイズ * GPU 数で乗算したものを返すことに注意
            return len(self.df_pairs) // (self.batch_size * self.n_gpus) * (self.batch_size * self.n_gpus)
    ```

- データローダーでの CPU数 `num_workers`<br>
    DDP では、GPU 数のプロセスに分割されるので、各プロセスでの データローダーでの CPU数 `num_workers` を DP のときと同じ値に設定すると、全プロセスでは `num_workers` * GPU 数 での CPU 数になってしまう。例えば、CPU x 4, GPU x 4 のマシンでは、4 x 4 = 16 個の CPU 数を設定していることになる。
    実際のマシンの CPU 数よりも大きな値にすると、データローダーでの動作が遅くなるので、`num_workers` は CPU 数を GPU 数で乗算したものなどを設定する必要がある。
    ```python
    dloader_train = torch.utils.data.DataLoader(sampler_train, batch_size=args.batch_size, sampler=sampler_train, shuffle=False, num_workers = args.n_workers//len(args.gpu_ids), pin_memory = True )
    ```

- tensorboard への表示処理・チェックポイントの保存・print() などは rank 0 でのみ行う<br>
    DDP では、マルチプロセス化された状態でプログラム（上記コード例では `train()` メソッド）が実行されるので、tensorboard への表示処理・チェックポイントの保存・print() などの処理も全プロセスでそれぞれ行われることになる。一般的には、tensorboard への表示処理・チェックポイントの保存・print() などの処理は、マスタープロセス（rank0）のみで行えばよいので、`if(rank==0)` の条件を入れるなどして、マスタープロセスでのみ行うようにしたほうがよい    
    ```python
    model_G = Pix2PixHDGenerator().to(device)
    # 最初のプロセスのみで表示処理を行うようにする
    if( rank == 0 ):
        print( "model_G\n", model_G )
    ```
    ```python
    # 最初のプロセスのみで表示処理を行うようにする
    if( args.local_rank == 0 ):
        board_train = SummaryWriter( log_dir = os.path.join(args.tensorboard_dir, args.exper_name) )

    ...

    if( rank == 0 ):
        board_train.add_scalar('G/loss_G', loss_G.item(), step)
    ```

## `python -m torch.distributed.launch` でプロセスを複数個起動させる場合
`python -m torch.distributed.launch` を用いて、プロセスを複数個起動させて DDP を行う方法もある。
こちらの方法では、`torch.multiprocessing.spawn()` のときのように、マルチプロセスを行うメソッドを指定しなくてよいので、DDP を行わないコードから最小限の修正で DDP を行うコードを実装できるというメリットがある。

- 学習スクリプト例 `train_ddp2.py`
    ```python
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        ...        
        parser.add_argument("--gpu_ids", default="0,1,2,3", help="使用GPU番号")
        parser.add_argument("--local_rank", type=int, help="DDP [DistributedDataParallel] の使用時のマルチプロセス番号。python -m torch.distributed.launch で自動的に設定される")
        parser.add_argument('--debug', action='store_true')
        args = parser.parse_args()

        str_gpu_ids = args.gpu_ids.split(',')
        args.gpu_ids = []
        for str_gpu_id in str_gpu_ids:
            gpu_id = int(str_gpu_id)
            if gpu_id >= 0:
                args.gpu_ids.append(gpu_id)

        # rank0（0番目のプロセス）マシンのアドレスとポート番号
        os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '1234'

        # すべてのプロセスが同じIPアドレスとポートを使用することで、マスターを介して調整できるようにする
        if( torch.cuda.is_available() ):
            dist.init_process_group("nccl", rank=args.local_rank, world_size=len(args.gpu_ids))
        else:
            dist.init_process_group("gloo", rank=args.local_rank, world_size=len(args.gpu_ids))

        # 実行 Device の設定
        if( torch.cuda.is_available() ):
            if( args.use_ddp ):
                torch.cuda.set_device(rank)
                device = torch.device(f'cuda:{rank}')
            else:
                device = torch.device(f'cuda:{args.gpu_ids[0]}')

            print( "実行デバイス :", device)
            print( "GPU名 :", torch.cuda.get_device_name(device))
            print("torch.cuda.current_device() =", torch.cuda.current_device())
        else:
            device = torch.device("cpu")
            print( "実行デバイス :", device)

        ...

        #================================
        # データセットの読み込み
        #================================    
        # 学習用データセットとテスト用データセットの設定
        ds_train = TempleteDataset( args, args.dataset_dir, datamode = "train", image_height = args.image_height, image_width = args.image_width, batch_size = args.batch_size, data_augument_types = args.data_augument_types, use_ddp = args.use_ddp, n_gpus = len(args.gpu_ids), debug = args.debug )

        #sampler_train = torch.utils.data.distributed.DistributedSampler(ds_train, num_replicas=len(args.gpu_ids), rank=rank, shuffle=True)
        sampler_train = torch.utils.data.distributed.DistributedSampler(ds_train, num_replicas=len(args.gpu_ids), rank=rank)

        dloader_train = torch.utils.data.DataLoader(sampler_train, batch_size=args.batch_size, sampler=sampler_train, shuffle=False, num_workers = args.n_workers//len(args.gpu_ids), pin_memory = True )

        #================================
        # モデルの構造を定義する。
        #================================
        model_G = Pix2PixHDGenerator().to(device)
        if( args.debug ):
            if( rank == 0 ):
                print( "model_G\n", model_G )

        #================================
        # optimizer_G の設定
        #================================
        optimizer_G = optim.Adam( params = model_G.parameters(), lr = args.lr, betas = (args.beta1,args.beta2) )

        #================================
        # マルチ GPU
        #================================
        model_G = torch.nn.parallel.DistributedDataParallel(model_G, device_ids=[rank])

        #================================
        # loss 関数の設定
        #================================
        loss_fn = nn.L1Loss()

        #================================
        # モデルの学習
        #================================    
        step = 0
        for epoch in tqdm( range(args.n_epoches), desc = "epoches" ):
            for iter, inputs in enumerate( tqdm( dloader_train, desc = "epoch={}".format(epoch) ) ):
                model_G.train()

                # 一番最後のミニバッチループで、バッチサイズに満たない場合は無視する（後の計算で、shape の不一致をおこすため）
                if inputs["image"].shape[0] != args.batch_size:
                    break

                # ミニバッチデータを GPU へ転送
                image = inputs["image"].to(device)
                target = inputs["target"].to(device)

                #----------------------------------------------------
                # 生成器 の forword 処理
                #----------------------------------------------------
                output = model_G( image )
                if( args.debug and n_print > 0 ):
                    print( "output.shape : ", output.shape )

                #----------------------------------------------------
                # 生成器の更新処理
                #----------------------------------------------------
                # 損失関数を計算する
                loss_G = loss_fn( output, target )

                # ネットワークの更新処理
                optimizer_G.zero_grad()
                loss_G.backward()
                optimizer_G.step()

                #====================================================
                # 学習過程の表示
                #====================================================
                if( step == 0 or ( step % args.n_diaplay_step == 0 ) ):
                    # 最初のプロセスのみで表示処理を行うようにする
                    if( rank == 0 ):
                        # lr
                        for param_group in optimizer_G.param_groups:
                            lr = param_group['lr']

                        board_train.add_scalar('lr/learning rate', lr, step )

                        # loss
                        board_train.add_scalar('G/loss_G', loss_G.item(), step)
                        print( "step={}, loss_G={:.5f}".format(step, loss_G.item()) )

                        # visual images
                        visuals = [
                            [ image.detach(), target.detach(), output.detach() ],
                        ]
                        board_add_images(board_train, 'train', visuals, step+1)

        return
    ```

- 起動スクリプト例
    ```sh
    GPU_IDS="0,1,2,3"
    N_GPUS=4
    python -m torch.distributed.launch \
        --nproc_per_node ${N_GPUS} --nnodes=1 --node_rank=0 \
        --master_addr="localhost" --master_port=1234 \
        train_ddp2.py \
            --gpu_ids ${GPU_IDS} \
            --debug
    ```

ポイントは以下の通り。その他のポイントは `torch.multiprocessing.spawn()` を使用する場合と同様

- args 引数 `--local_rank` の追加<br>
    `python -m torch.distributed.launch` でスクリプトを起動した場合は、環境変数 `LOCAL_RANK` または `--local_rank` という コマンドライン引数を与えた状態でスクリプトが起動される。そのため、スクリプト内にて args 引数 `parser.add_argument("--local_rank", type=int)` を追加する必要がある。<br>
    この `--local_rank` は、`torch.multiprocessing.spawn()` のときの第１引数で指定した `rank` と同じ処理になるように設定すればよい

- xxx

## ■ 参考サイト
- https://qiita.com/meshidenn/items/1f50246cca075fa0fce2
- https://colab.research.google.com/github/YutaroOgawa/pytorch_tutorials_jp/blob/main/notebook/6_Parallel_Distributed/6_3_getting_started_with_distributed_data_parallel_jp.ipynb
- https://qiita.com/kamo-naoyuki/items/2671768aa92c4efb4118
- https://deideeplearning.com/2020/04/05/pytorch-distributed/