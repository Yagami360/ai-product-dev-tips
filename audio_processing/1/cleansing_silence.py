import os
import sys
import argparse

from pydub import AudioSegment
from pydub.silence import split_on_silence
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_audio_file', type=str, default="in_audio/1.mp3", help="入力音声のディレクトリ")
    parser.add_argument('--out_audio_file', type=str, default="out_audio/1.mp3", help="出力音声のディレクトリ")
    parser.add_argument('--min_silence_len', type=int, default=1500, help="")
    parser.add_argument('--silence_thresh', type=int, default=-30, help="")
    parser.add_argument('--keep_silence', type=int, default=500, help="")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    # 音声データの分割
    audio_chunks = split_on_silence(
        AudioSegment.from_file(args.in_audio_file),
        min_silence_len = args.min_silence_len,           # min_silence_len で指定した ms 以上の無音がある箇所で分割
        silence_thresh = args.silence_thresh,             # silence_thresh で指定した dBFS 以下で無音とみなす
        keep_silence = args.keep_silence                  # 分割後 keep_silence で指定した ms だけ、無音を残す
    )
    print( "len(audio_chunks) : ", len(audio_chunks) )

    # 分割した音声データを保存
    audio_file_paths = []
    for i, chunk in enumerate(audio_chunks):
        audio_file_path = args.out_audio_file.split(".")[0] + "_" + str(i) + "." + args.out_audio_file.split(".")[-1]
        chunk.export(audio_file_path)
        audio_file_paths.append(audio_file_path)

    # 分割した音声データを結合
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
    print(*commands_i)

    subprocess.call([
        'ffmpeg', '-y',
#        '-i', audio_file_paths[0],
        *commands_i,
        '-filter_complex', "concat=n={}:v=0:a=1".format(len(audio_file_paths)),
        args.out_audio_file
    ])
