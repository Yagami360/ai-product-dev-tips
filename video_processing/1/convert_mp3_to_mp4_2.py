import os
import sys
import argparse
from tqdm import tqdm 
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_image_file', type=str, default="in_image/1.jpg", help="入力画像のディレクトリ")
    parser.add_argument('--in_audio_file', type=str, default="in_audio/1.mp3", help="入力音声のディレクトリ")
    parser.add_argument('--out_video_file', type=str, default="out_video/1.mp4", help="出力動画のディレクトリ")
    parser.add_argument('--fps', type=int, default=10, help="出力動画のFPS")
    parser.add_argument('--format', type=str, default="yuv420p", help="出力 mp4 動画のフォーマット")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    #--------------------
    # 変換処理
    #--------------------
    command = [
        'ffmpeg',
        '-i', '{}'.format(args.in_image_file),
        '-i', '{}'.format(args.in_audio_file),
        '-map', '0:v',
        '-map', '1:a',
        '-loop', '1',
        '-framerate', '1',
        '-r', '{}'.format(args.fps),
        '-vf', "scale='iw-mod(iw,2)':'ih-mod(ih,2)',format={}".format(args.format),
    ]

    subprocess.call(command, shell=True)
    """
    vf = "scale='iw-mod(iw,2)':'ih-mod(ih,2)',format={}".format(args.format)
    subprocess.call(
        'ffmpeg -y \
            -i {} -i {} \
            -map 0:v -map 1:a \
            -loop 1 \
            -framerate 1 -r {} \
            -vf {} \
            -movflags +faststart -shortest -fflags +shortest -max_interleave_delta 100M \
            {}'.format(args.in_image_file, args.in_audio_file, args.fps, vf, args.out_video_file),
        shell=True
    )
    """
