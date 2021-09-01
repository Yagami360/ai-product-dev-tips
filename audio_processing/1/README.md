# pydub と ffmpeg を用いて音声ファイルの無音部分をクレンジングする

## ■ 方法

1. ffmpeg コマンドをインストールする
    - MacOS の場合
        ```sh
        $ brew install ffmpeg
        ```
    - Ubuntu の場合
        ```sh
        $ sudo apt install ffmpeg
        ```

1. python モジュールの `pydub` をインストールする
    ```sh
    $ pip install pydub
    ```

1. python モジュールの `pydub` にある `split_on_silence` で無音部分で音声ファイルを分割する
    ```python
    # 抜粋コード
    from pydub import AudioSegment
    from pydub.silence import split_on_silence

    audio_chunks = split_on_silence(
        AudioSegment.from_file(args.in_audio_file),
        min_silence_len = args.min_silence_len,           # min_silence_len で指定した ms 以上の無音がある箇所で分割
        silence_thresh = args.silence_thresh,             # silence_thresh で指定した dBFS 以下で無音とみなす
        keep_silence = args.keep_silence                  # 分割後 keep_silence で指定した ms だけ、無音を残す
    )
    print( "len(audio_chunks) : ", len(audio_chunks) )
    ```

1. 分割した音声ファイルを保存する
    ```python
    audio_file_paths = []
    for i, chunk in enumerate(audio_chunks):
        audio_file_path = args.out_audio_file.split(".")[0] + "_" + str(i) + "." + args.out_audio_file.split(".")[-1]
        chunk.export(audio_file_path)
        audio_file_paths.append(audio_file_path)
    ```

1. ffmpeg を用いて分割した音声ファイルを結合する
    ```python
    import subprocess

    # -i : 入力File名（必要数記載）
    # -filter_complex : 複合フィルタ（ビデオ、オーディオ混合フィルタ定義）
    # concat : 動画・音声を連結するフィルタ定義
    # n : 連結するファイル数(入力File名で指定した数を記載)
    # v : 出力する映像ストリーム数
    # a : 出力する音声ストリーム数
    commands_i = []
    for audio_file_path in audio_file_paths:
        commands_i.append("-i")
        commands_i.append(audio_file_path)

    subprocess.call([
        'ffmpeg', '-y',
        *commands_i,
        '-filter_complex', "concat=n={}:v=0:a=1".format(len(audio_file_paths)),
        args.out_audio_file
    ])
    ```

    > `ffmpeg -i input1.mp3 -i input2.mp3 -filter_complex “concat=n=2:v=0:a=1” output.mp3` のように、`-i` を複数回設定することで、複数の音声ファイルを結合できる。今の場合、入力ファイルによって分割さえる音声ファイル数が不定なので、`commands_i` に `["-i", "1_1.mp3", "-i", "1_2.mp3" "-i", "1_3.mp3"]` のようなリストデータを保管し、リストのアンパック `*commands_i` で `ffmpeg` コマンドの `-i` 引数を設定している。

## ■ 参考サイト
- https://chachay.hatenablog.com/entry/2016/10/03/215841
- https://www.21064.com/2018/12/06/ffmpeg-%E9%9F%B3%E5%A3%B0%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E9%80%A3%E7%B5%90%E3%81%99%E3%82%8B/