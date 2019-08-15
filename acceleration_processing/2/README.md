## 【Python】for ループ内の処理を複数 CPU の並列処理で高速化する。

- 機械学習タスクの特に前処理では、GPU ではなく CPU で処理を行うことが多くなるが、for ループで大量のデータを前処理する場合に時間がかかる。

- このような場合に、Python の `joblib` や `multiprocessing` モジュールを利用して for ループでの前処理の CPU の並列化処理を行うと、処理を高速化することが出来るケースが多々存在する。（※必ずしも高速化されるとは限らず、場合によっては速度が遅くなってしまうケースも存在することに注意）

- `multiprocessing` を使用した for ループ内の CPU 並列化処理。
    - `multiprocessing` の使い方は、`image_resize.py` と `image_resize_parallel.py` の実装を比較すると分かりやすい。
    ```python
    from multiprocessing import Pool
    ...
    image_names = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.png'))]
    ...

    def wrapper(args):
        return process(*args)

    def process(image_dir, image_out_dir, image_name):
        # for ループ内処理
        ...
        if( hoge ):
            return -1 # 異常終了ケース

        return 0 # 正常終了ケース

    # process() に渡す、引数リスト
    args_list = [ [image_dir, image_out_dir, image_names[i]] for i in range(len(image_names)) ]

    process_num = None  # None で利用可能な CPU の最大数
    with Pool(process_num) as p:
        imap = p.imap(wrapper, args_list)
        output = list(tqdm(imap, total=len(args_list)))

    n_ok = output.count(0)      # return 0 の個数
    n_ng = output.count(-1)     # rerutn 1 の個数
    ```