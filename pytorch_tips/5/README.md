# 【PyTorch】AMP [Automatic Mixed Precision] を使用した学習と推論の高速化


## ■ `apex.amp` 使用時

## ◎ AMP のインストール

[AMP の 公式 GitHub レポジトリ](https://github.com/NVIDIA/apex#quick-start) を参照のこと。

C++ でビルドしていない python 版　AMP であれば、以下の conda コマンドでもインストール可能。使用メモリが半減されるが、処理速度は C++ でビルドしたものよりも遅くなる。
```sh
$ conda install -c conda-forge nvidia-apex
```

## ◎ 単一の optimizer で構成されるモデルの場合

- 学習スクリプトのコード例
    ```python
    from apex import amp
    ...

    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        ...
        parser.add_argument("--gpu_ids", default="0", help="使用GPU番号")
        args = parser.parse_args()

        # 実行 Device の設定
        if( torch.cuda.is_available() ):
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
        ds_train = TempleteDataset( args, args.dataset_dir, datamode = "train", image_height = args.image_height, image_width = args.image_width, data_augument_types = args.data_augument_types, debug = args.debug )
        dloader_train = torch.utils.data.DataLoader(ds_train, batch_size=args.batch_size, shuffle=True, num_workers = args.n_workers, pin_memory = True )

        #================================
        # モデルの構造を定義する。
        #================================
        model_G = Pix2PixHDGenerator().to(device)

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
        # loss 関数の設定
        #================================
        loss_fn = nn.L1Loss()

        #================================
        # モデルの学習
        #================================    
        print("Starting Training Loop...")
        n_print = 1
        step = 0
        for epoch in tqdm( range(args.n_epoches), desc = "epoches" ):
            for iter, inputs in enumerate( tqdm( dloader_train, desc = "epoch={}".format(epoch) ) ):
                model_G.train()

                # 一番最後のミニバッチループで、バッチサイズに満たない場合は無視する（後の計算で、shape の不一致をおこすため）
                if inputs["image_s"].shape[0] != args.batch_size:
                    break

                # ミニバッチデータを GPU へ転送
                image_s = inputs["image_s"].to(device)
                image_t = inputs["image_t"].to(device)

                #----------------------------------------------------
                # 生成器 の forword 処理
                #----------------------------------------------------
                output = model_G( image_s )

                #----------------------------------------------------
                # 生成器の更新処理
                #----------------------------------------------------
                # 損失関数を計算する
                loss_G = loss_fn( output, image_t )

                # ネットワークの更新処理
                optimizer_G.zero_grad()
                with amp.scale_loss(loss_G, optimizer_G, loss_id=0) as loss_G_scaled:
                    loss_G_scaled.backward()
                optimizer_G.step()
    ```

- 推論スクリプトのコード例
    ```python
    from apex import amp
    ...

    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        ...
        parser.add_argument("--gpu_ids", default="0", help="使用GPU番号")
        args = parser.parse_args()

        # 実行 Device の設定
        if( torch.cuda.is_available() ):
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
        ds_test = TempleteDataset( args, args.dataset_dir, datamode = "test", image_height = args.image_height, image_width = args.image_width, data_augument_types = "resize,crop", debug = args.debug )
        dloader_test = torch.utils.data.DataLoader(ds_test, batch_size=args.batch_size_test, shuffle = False, num_workers = args.n_workers, pin_memory = True )

        #================================
        # モデルの構造を定義する。
        #================================
        model_G = Pix2PixHDGenerator().to(device)

        # モデルを読み込む
        if not args.load_checkpoints_path == '' and os.path.exists(args.load_checkpoints_path):
            load_checkpoint(model_G, device, args.load_checkpoints_path )

        #================================
        # optimizer_G の設定（ダミー）
        #================================
        optimizer_G = optim.Adam( params = model_G.parameters(), lr = 0.0001, betas = (0.999,0.5) )

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
        # モデルの推論
        #================================    
        print("Starting Testing Loop...")
        n_print = 1
        model_G.eval()
        for step, inputs in enumerate( tqdm( dloader_test, desc = "Samplings" ) ):
            if inputs["image_s"].shape[0] != args.batch_size_test:
                break

            # ミニバッチデータを GPU へ転送
            image_s_name = inputs["image_s_name"]
            image_s = inputs["image_s"].to(device)
            if( args.debug and n_print > 0):
                print( "image_s.shape : ", image_s.shape )

            #----------------------------------------------------
            # 生成器の推論処理
            #----------------------------------------------------
            with torch.no_grad():
                output = model_G( image_s )
                if( args.debug and n_print > 0 ):
                    print( "output.shape : ", output.shape )

            #====================================================
            # 推論結果の保存
            #====================================================
            save_image_w_norm( output, os.path.join( args.results_dir, args.exper_name, "output", image_s_name[0] ) )

            # tensorboard
            visuals = [
                [ image_s, output ],
            ]
            board_add_images(board_test, 'test', visuals, step+1)

            n_print -= 1
            if( step >= args.n_samplings ):
                break
    ```

ポイントは、以下の通り

- AMP の初期化<br>
    ```python
    model_G, optimizer_G = amp.initialize(
        model_G, 
        optimizer_G, 
        opt_level = 'O1',
        num_losses = 1
    )
    ```

    単一の optimizer で構成されるモデルの場合は、`amp.initialize()` の第１引数と第２引数に、それぞれモデルと optimerzer を設定すればよい。
    また `num_losses` には、1 を設定すればよい

    `opt_level` の値の意味は以下の通りで、基本的には `"O1"` を設定すればよい。 
    > `"O1"` の場合、モデルの種類にもよるが、モデルの使用 GPU メモリ量がおよそ半減となり、学習時間がおよそ 1.5 倍高速化されることが多い。

    - `"O0"` : FP32 を使用（AMP を使用しないときと同じ）
    - `"O1"` : FP16 と FP32 の Mixed Precision を行う。(推奨設定値)
    - `"O2"` : 殆どが FP16 で構成され、一部が FP32 の Mixed Precision を行う。
    - `"O3"` : FP16 のみを使用

- スケーリングされた loss 値での誤差逆伝播法処理<br>
    FP16 にスケーリングされた loss 値で誤差逆伝播法処理を行う。
    `num_losses` を 1 に設定した場合は、`amp.scale_loss()` の `loss_id` には 0 を設定する。

    ```python
    # ネットワークの更新処理
    optimizer_G.zero_grad()
    with amp.scale_loss(loss_G, optimizer_G, loss_id=0) as loss_G_scaled:
        loss_G_scaled.backward()
    optimizer_G.step()
    ```

- 推論時にも AMP を適用する場合は、ダミーの optimizer を設定。<br>
    AMP は、学習時だけでなく推論時にも適用可能であり、学習時と同じ用に消費 GPU メモリと推論処理時間の高速化の恩恵が得られる。

    推論時には学習を行わないので、optimizer は定義しないのが一般的であるが、AMP を初期化する際には、optimizer を指定する必要があるので、ダミーの optimizer を定義した上で AMP の初期化を行うようにする。

    ```python
    # ダミーの optimizer
    optimizer_G = optim.Adam( params = model_G.parameters(), lr = 0.0001, betas = (0.999,0.5) )

    # AMP の初期化
    model_G, optimizer_G = amp.initialize(
        model_G, 
        optimizer_G, 
        opt_level = 'O1',
        num_losses = 1
    )
    ```

### ◎ 複数の optimizer で構成されるモデルの場合
GAN のように複数モデル（生成器 + 識別器）と複数の optimizer（生成器の optimizer + 識別器の optimizer）が存在する場合は、`amp.initialize()` での AMP 初期化方法と `amp.scale_loss()` での `loss_id` の設定方法が少し変わってくる
 
- 学習スクリプトの例
    ```python
    from apex import amp
    ...

    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        ...
        parser.add_argument("--gpu_ids", default="0", help="使用GPU番号")
        args = parser.parse_args()

        # 実行 Device の設定
        if( torch.cuda.is_available() ):
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
        ds_train = TempleteDataset( args, args.dataset_dir, datamode = "train", image_height = args.image_height, image_width = args.image_width, data_augument_types = args.data_augument_types, debug = args.debug )
        dloader_train = torch.utils.data.DataLoader(ds_train, batch_size=args.batch_size, shuffle=True, num_workers = args.n_workers, pin_memory = True )

        #================================
        # モデルの構造を定義する。
        #================================
        model_G = Pix2PixHDGenerator().to(device)
        model_D = PatchGANDiscriminator( in_dim = 3+3, n_fmaps = 64 ).to( device )

        #================================
        # optimizer_G の設定
        #================================
        optimizer_G = optim.Adam( params = model_G.parameters(), lr = args.lr, betas = (args.beta1,args.beta2) )
        optimizer_D = optim.Adam( params = model_D.parameters(), lr = args.lr, betas = (args.beta1,args.beta2) )

        #================================
        # apex initialize
        #================================
        [model_D, model_G], [optimizer_D, optimizer_G] = amp.initialize(
            [model_D, model_G], 
            [optimizer_D, optimizer_G], 
            opt_level = args.opt_level,
            num_losses = 2
        )

        #================================
        # loss 関数の設定
        #================================
        loss_l1_fn = nn.L1Loss()
        loss_vgg_fn = VGGLoss(device, n_channels=3)
        loss_adv_fn = LSGANLoss(device)

        #================================
        # モデルの学習
        #================================    
        print("Starting Training Loop...")
        n_print = 1
        step = 0
        for epoch in tqdm( range(args.n_epoches), desc = "epoches" ):
            for iter, inputs in enumerate( tqdm( dloader_train, desc = "epoch={}".format(epoch) ) ):
                model_G.train()
                model_D.train()

                # 一番最後のミニバッチループで、バッチサイズに満たない場合は無視する（後の計算で、shape の不一致をおこすため）
                if inputs["image_s"].shape[0] != args.batch_size:
                    break

                # ミニバッチデータを GPU へ転送
                image_s = inputs["image_s"].to(device)
                image_t = inputs["image_t"].to(device)
                
                #----------------------------------------------------
                # 生成器 の forword 処理
                #----------------------------------------------------
                output = model_G( image_s )

                #----------------------------------------------------
                # 識別器の更新処理
                #----------------------------------------------------
                # 無効化していた識別器 D のネットワークの勾配計算を有効化。
                for param in model_D.parameters():
                    param.requires_grad = True

                # 学習用データをモデルに流し込む
                d_real = model_D( torch.cat([image_s, image_t], dim=1) )
                d_fake = model_D( torch.cat([image_s, output.detach()], dim=1) )

                # 損失関数を計算する
                loss_D, loss_D_real, loss_D_fake = loss_adv_fn.forward_D( d_real, d_fake )

                # ネットワークの更新処理
                optimizer_D.zero_grad()
                with amp.scale_loss(loss_D, optimizer_D, loss_id=0) as loss_D_scaled:
                    loss_D_scaled.backward(retain_graph=True)
                optimizer_D.step()

                # 無効化していた識別器 D のネットワークの勾配計算を有効化。
                for param in model_D.parameters():
                    param.requires_grad = False

                #----------------------------------------------------
                # 生成器の更新処理
                #----------------------------------------------------
                # 損失関数を計算する
                loss_l1 = loss_l1_fn( image_t, output )
                loss_vgg = loss_vgg_fn( image_t, output )
                loss_adv = loss_adv_fn.forward_G( d_fake )
                loss_G =  args.lambda_l1 * loss_l1 + args.lambda_vgg * loss_vgg + args.lambda_adv * loss_adv

                # ネットワークの更新処理
                optimizer_G.zero_grad()
                with amp.scale_loss(loss_G, optimizer_G, loss_id=1) as loss_G_scaled:
                    loss_G_scaled.backward()
                optimizer_G.step()
    ```

ポイントは、以下の通り

- AMP の初期化<br>
    ```python
    [model_D, model_G], [optimizer_D, optimizer_G] = amp.initialize(
        [model_D, model_G], 
        [optimizer_D, optimizer_G], 
        opt_level = 'O1',
        num_losses = 2
    )
    ```

    複数の optimizer で構成されるモデルの場合は、`amp.initialize()` の第１引数と第２引数に、それぞれ複数のモデルのリストと 複数の optimerzer のリストを設定すればよい。
    また `num_losses` には、基本的には optimerzer の数と同じ値（この例では 2）を設定すればよい


- スケーリングされた loss 値での誤差逆伝播法処理<br>
    ```python
    #-----------------
    # 識別器の学習処理
    #-----------------
    ...

    # ネットワークの更新処理
    optimizer_D.zero_grad()
    with amp.scale_loss(loss_D, optimizer_D, loss_id=0) as loss_D_scaled:
        loss_D_scaled.backward(retain_graph=True)
    optimizer_D.step()

    ...

    #-----------------
    # 生成器の学習処理
    #-----------------
    ...

    # ネットワークの更新処理
    optimizer_G.zero_grad()
    with amp.scale_loss(loss_G, optimizer_G, loss_id=1) as loss_G_scaled:
        loss_G_scaled.backward()                
    optimizer_G.step()

    ...
    ```
    複数の optimizer で構成されるモデルの場合は、それぞれの optimizer に対応した loss 値を `loss_id` の値を変えながら、amp.scale_loss() を使ってスケーリングする。
    `num_losses` を 2 に設定した場合は、有効な `loss_id` の値は 0 or 1 になる。

## ■ `torch.cuda.amp` 使用時（pytorch 1.6 以降のみ使用可能）

xxx
