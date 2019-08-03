> `split_files.py` と `concat_files.py` の実装が分かりにくく、また単調である。もっといい実装はないか検討

- `$ export CUDA_VISIBLE_DEVICES` で複数の GPU で処理を行う場合、以下のシェルスクリプト例のように、それぞれのGPUが処理するフォルダを分けておく必要がある。
    ```sh
    # 4 台の GPU で処理する場合の処理例
    export CUDA_VISIBLE_DEVICES=0   # 0番目の GPU を指定
    python gpu_processing dir0      # dir0 で入力データの0番目の分割したフォルダを指定

    export CUDA_VISIBLE_DEVICES=1   # 1番目の GPU を指定
    python gpu_processing dir1      # dir1 で入力データの1番目の分割したフォルダを指定

    export CUDA_VISIBLE_DEVICES=2
    python gpu_processing dir2

    export CUDA_VISIBLE_DEVICES=3
    python gpu_processing dir3
    ```
- このような用途で、機械学習の前処理では、入力データとして使用する１つのフォルダ内のファイルを複数のフォルダに均等に分割する処理がよく行われる。
- 一般的に、分割されたフォルダは、複数台でのGPU 処理の完了後、再び１つに統合される。
- これら一連の処理を行うシェルスクリプトの一例は、以下のようになる。
    ```sh
    # 4 台の GPU で処理する場合の処理例
    python split_files.py in_dir in_dir --n_split 4   # フォルダを分割するスクリプト

    export CUDA_VISIBLE_DEVICES=0   # 0番目の GPU を指定
    python gpu_processing 00 &      # 末端に & で別プロセスで実行

    export CUDA_VISIBLE_DEVICES=1   # 1番目の GPU を指定
    python gpu_processing 01 &      # 末端に & で別プロセスで実行

    export CUDA_VISIBLE_DEVICES=2
    python gpu_processing 02 &

    export CUDA_VISIBLE_DEVICES=3
    python gpu_processing 03 &

    wait    # wait で上記４台の GPU 処理が完了するまで待つ

    python concat_files in_dir in_dir --n_split 4     # 分割したフォルダを最統合
    ```