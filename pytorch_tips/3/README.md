# 【PyTorch】DDP [DistributedDataParallel] を使用した複数プロセス + 複数GPU での高速化

DP では、１つのプロセスを複数の GPU で動作させるような並列化処理であり、誤差逆伝播法の処理のみを並列化した処理になっている。<br>
一方 DDP では、１つのプロセスに対して１つの GPU で動作させるような並列化処理になっている（例えば、４つの GPU で学習する場合は、４つのプロセスが動作し、各々のプロセスで１つの GPU が動作する処理となる。）また、誤差逆伝播の処理以外にもデータローダーでの処理も並列化するという違いもある。

これにより、DDP は DP を利用した高速化に比べて、より高速化することができる。
但し、DP を使用した場合に比べて、実装が面倒になるというデメリットや消費メモリが多くなるというデメリットはある。

PYtoch での DDP は、`torch.nn.parallel.DistributedDataParallel()`, `torch.utils.data.distributed.DistributedSampler()` を使用することで実現できる。
また DDP を行うための複数プロセス化は、`torch.multiprocessing.spawn()` または `python -m torch.distributed.launch` を使用することで実現できる

## `torch.multiprocessing.spawn()` でプロセスを複数個起動させる場合

- コード例 : `train_ddp.py` から抜粋
    ```python
    ```

- ポイント
    - `dist.init_process_group()` : 
        - バックエンドには、GPU での分散学習の場合は `nccl` を設定し、CPU での分散学習の場合は `gloo` を設定するのが一般的

    - ``


## `python -m torch.distributed.launch` でプロセスを複数個起動させる場合

- コード例
    ```python
    ```

- ポイント
    - `python -m torch.distributed.launch` でスクリプトを起動した場合は、環境変数 `LOCAL_RANK` または `--local_rank` という コマンドライン引数を与えた状態でスクリプトが起動される。そのため、スクリプト内にて args 引数 `parser.add_argument("--local_rank", type=int)` を追加する必要がある。

    - xxx

## ■ 参考サイト
- https://qiita.com/meshidenn/items/1f50246cca075fa0fce2
- https://colab.research.google.com/github/YutaroOgawa/pytorch_tutorials_jp/blob/main/notebook/6_Parallel_Distributed/6_3_getting_started_with_distributed_data_parallel_jp.ipynb
- https://qiita.com/kamo-naoyuki/items/2671768aa92c4efb4118
- https://deideeplearning.com/2020/04/05/pytorch-distributed/