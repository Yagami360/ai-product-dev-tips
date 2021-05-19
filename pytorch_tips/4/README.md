# 【PyTorch】DDP + AMP を使用した高速化

## ■ `apex.amp` 使用時

AMP [Automatic Mixed Precision] と DDP を同時に使用する場合は、「[【PyTorch】DDP [DistributedDataParallel] を使用した複数プロセス + 複数GPU での高速化](https://github.com/Yagami360/MachineLearning_Tips/tree/master/pytorch_tips/3)」記載の方法に対して、`torch.nn.parallel.DistributedDataParallel` を `apex.parallel.DistributedDataParallel` に置き換えた上で、AMP の設定をすれば良い

- 学習スクリプトのコード例（一部抜粋）
    ```python
    import apex
    from apex import amp
    ...

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
        # apex initialize
        #================================
        model_G, optimizer_G = amp.initialize(
            model_G, 
            optimizer_G, 
            opt_level = args.opt_level,
            num_losses = 1
        )

        #================================
        # マルチ GPU
        #================================
        model_G = apex.parallel.DistributedDataParallel(model_G)

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
                with amp.scale_loss(loss_G, optimizer_G, loss_id=0) as loss_G_scaled:
                    loss_G_scaled.backward()
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
        parser.add_argument('--opt_level', choices=['O0','O1','O2','O3'], default='O1', help='mixed precision calculation mode')
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

ポイントは、以下の通り。その他ポイントは、「[【PyTorch】DDP [DistributedDataParallel] を使用した複数プロセス + 複数GPU での高速化](https://github.com/Yagami360/MachineLearning_Tips/tree/master/pytorch_tips/3)」記載のポイントと同様


- APM の初期化<br>
    DDP なしのときの AMP と同様に、AMP を初期化する
    ```python
    model_G, optimizer_G = amp.initialize(
        model_G, 
        optimizer_G, 
        opt_level = 'O1',
        num_losses = 1
    )
    ```

- `apex.parallel.DistributedDataParallel` でモデルを並列化<br>
    AMP なしのときの DDP では、`torch.nn.parallel.DistributedDataParallel` でモデルを並列化したが、AMP ありの DDP の場合は `apex.parallel.DistributedDataParallel` でモデルを並列化する。
    この際に、`torch.nn.parallel.DistributedDataParallel` のときのように `device_ids` でマルチプロセスの `rank` を指定しないくてよいことに注意。これは、AMP では１プロセスに１GPUしか割り当てれないために不要になっていると思われる。
    ```python
    model_G = apex.parallel.DistributedDataParallel(model_G)
    ```

- スケーリングされた loss 値での誤差逆伝播法処理<br>
    DDP なしのときの AMP と同様に、FP16 にスケーリングされた loss 値で誤差逆伝播法処理を行う
    ```python
    # ネットワークの更新処理
    optimizer_G.zero_grad()
    with amp.scale_loss(loss_G, optimizer_G, loss_id=0) as loss_G_scaled:
        loss_G_scaled.backward()
    optimizer_G.step()
    ```
    

## ■ `torch.cuda.amp` 使用時（pytorch 1.6 以降のみ使用可能）

xxx
