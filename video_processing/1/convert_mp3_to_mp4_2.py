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
    #ffmpeg -y -loop 1 -i ${IN_IMAGE_FILE} -i ${IN_AUDIO_FILE} -vcodec libx264 -acodec aac -ab 160k -ac 2 -ar 48000 -pix_fmt yuv420p -shortest ${OUT_VIDEO_FILE}
    """
    subprocess.call([
        'ffmpeg', '-y',
        '-i', args.in_image_file,
        '-i', args.in_audio_file,
        '-map', '0:v', '-map', '1:a',
        '-loop', '1',
        '-framerate', '1', '-r', str(args.fps),
        '-vf', "scale='iw-mod(iw,2)':'ih-mod(ih,2)',format={}".format(args.format),
        '-movflags', '+faststart', '-shortest', '-fflags', '+shortest', '-max_interleave_delta', '100M',
        args.out_video_file,
    ])
    """
    subprocess.call([
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', args.in_image_file,
        '-i', args.in_audio_file,
        '-vcodec', 'libx264',                       # 動画コーデック
        '-acodec', 'aac',                           # 音声コーデック
        '-ab', '160k',                              # 音声ビットレート
        '-ac', '2',                                 # 音声チャンネル数
        '-ar', '48000',                             # 音声サンプリングレート
        '-pix_fmt', args.format,                    # 
        '-shortest',                                # 入力の短い方(音声)に動画時間を合わす
        args.out_video_file,
    ])
