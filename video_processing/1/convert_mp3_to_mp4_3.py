import os
import sys
import argparse
from tqdm import tqdm 
import ffmpeg

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_image_file', type=str, default="in_image/1.jpg", help="入力画像のディレクトリ")
    parser.add_argument('--in_audio_file', type=str, default="in_audio/1.mp3", help="入力音声のディレクトリ")
    parser.add_argument('--out_video_file', type=str, default="out_video/1.mp4", help="出力動画のディレクトリ")
    parser.add_argument('--fps', type=int, default=10, help="出力動画のFPS")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    #--------------------
    # 変換処理
    # ffmpeg \
    # -loop 1 \
    # -framerate 1 \
    # -i ${IN_IMAGE_FILE} -i ${IN_AUDIO_FILE} \
    # -map 0:v -map 1:a -r ${FPS} -vf "scale='iw-mod(iw,2)':'ih-mod(ih,2)',format=yuv420p" \
    # -movflags +faststart -shortest -fflags +shortest -max_interleave_delta 100M \
    # ${OUT_VIDEO_FILE}
    #--------------------
    """
    # 入力
    stream1 = ffmpeg.input(args.in_audio_file)
    stream2 = ffmpeg.input(args.in_image_file)

    # 出力
    stream = ffmpeg.overlay(stream1)
    stream = ffmpeg.overlay(stream2)
    stream = ffmpeg.output(stream, args.out_video_file, r=args.fps)

    # 実行
    ffmpeg.run(stream)
    """
    audio_file = ffmpeg.input(args.in_audio_file)
    image_file = ffmpeg.input(args.in_image_file)
    (
        ffmpeg
        .concat(
            audio_file.trim(start_frame=10, end_frame=40),
        )
        .overlay(image_file)
        .output(args.out_video_file, r=args.fps)
        .run()
    )
    