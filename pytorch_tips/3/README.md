# 【PyTorch】DDP [DistributedDataParallel] を使用した高速化

DDP [DistributedDataParallel] を行う `torch.nn.parallel.DistributedDataParallel()` を使用すれば、DP [DataParallel] を行う `torch.nn.DataParallel()` を使用した高速化よりも更に高速化することができる。但し、DP を使用した場合に比べて、実装が少々面倒になるというデメリットはある。

DP は

DDP は単一のGPU

- DDP の実装例

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

    ```



## ■ 参考サイト
- https://qiita.com/meshidenn/items/1f50246cca075fa0fce2
- https://colab.research.google.com/github/YutaroOgawa/pytorch_tutorials_jp/blob/main/notebook/6_Parallel_Distributed/6_3_getting_started_with_distributed_data_parallel_jp.ipynb