# 【PyTorch】DP [DataParallel] を使用した 複数 GPU での並列学習と高速化
pytorch では、以下のスクリプトのように `torch.nn.DataParallel()` を使って、簡単に複数の GPU での並列学習を実現できる。

- DP [DataParallel] を使用した 複数 GPU での並列学習の実装例
    ```python
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu_ids", default="0,1,2,3", help="使用GPU番号")
    args = parser.parse_args()

    #os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_ids
    str_gpu_ids = args.gpu_ids.split(',')
    args.gpu_ids = []
    for str_gpu_id in str_gpu_ids:
        gpu_id = int(str_gpu_id)
        if gpu_id >= 0:
            args.gpu_ids.append(gpu_id)  

    #-----------------------------
    # 実行 Device の設定
    #-----------------------------
    if( torch.cuda.is_available() ):
        if(len(args.gpu_ids) > 2 ):
            device = torch.device(f'cuda:{args.gpu_ids[0]}')
        else:
            device = torch.device(f'cuda:{gpu_id}')

        print( "実行デバイス :", device)
        print( "GPU名 :", torch.cuda.get_device_name(device))
        print("torch.cuda.current_device() =", torch.cuda.current_device())
    else:
        device = torch.device("cpu")
        print( "実行デバイス :", device)

    #-----------------------------
    # モデル定義
    #-----------------------------
    model = Network().to(device)

    #-----------------------------
    # マルチ GPU
    #-----------------------------
    if len(args.gpu_ids) >= 2:
        model = torch.nn.DataParallel(model)
    ```

但し、`torch.nn.DataParallel()` を使うと、モデルのパラメーター名の先頭に `module.` が追加されるので、`torch.save(model.cpu().state_dict(), save_path)` で学習済みチェックポイントをそのまま保存した場合、`load_state_dict()` で学習済みチェックポイントを読み込むと以下のようなエラーが発生する
```sh
KeyError: 'unexpected key "module.xx.xx.weight" in state_dict'
```

このエラーの解決方法としては、以下の２つの方法がある。

1. `torch.save()` する際に `module.` を除外<br>
    `torch.save(model.cpu().state_dict(), save_path)` ではなく `torch.save(model.module.cpu().state_dict(), save_path)` とすることで、学習済みチェックポイントの各パラメーターに `module.` が追加されないようにする。

2. 学習済みチェックポイントの読み込み時に、各パラメーターの `module.` を除外<br>
    `module.` を除外せずにチェックポイントを保存した場合は、以下のスクリプトのように、モデルのパラメーターの各 key に値して `key.replace('module.', '')` などで `module.` を除外した上で、`load_state_dict()` すればよい
    ```python
    from collections import OrderedDict
    def load_checkpoint_multiGPU(model, checkpoint_path, > model_state_dict=True):
        if not os.path.exists(checkpoint_path):
            return
            
        state_dict = torch.load(checkpoint_path, map_location=torch.device('cpu'))
        new_state_dict = OrderedDict()
        if( model_state_dict ):
            for k, v in state_dict["model_state_dict"].items():
                if 'module' in k:
                    k = k.replace('module.', '')
                new_state_dict[k] = v
        else:
            for k, v in state_dict.items():
                if 'module' in k:
                    k = k.replace('module.', '')
                new_state_dict[k] = v
        model.load_state_dict(new_state_dict)
        return
    ```
