import os
import sys
import argparse
import json
from PIL import Image
from tqdm import tqdm 
import requests
import time

# 自作モジュール
from api.utils.utils import conv_base64_to_pillow, conv_pillow_to_base64

# グローバル変数
IMAGE_EXTENSIONS = ('.jpg', ".png",)
VIDEO_EXTENSIONS = ('.mp4',)
AUDIO_EXTENSIONS = ('.mp3',)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="0.0.0.0", help="API サーバーのホスト名（コンテナ名 or コンテナ ID）")
    parser.add_argument('--port', type=str, default="5000", help="API サーバーのポート番号")
    parser.add_argument('--in_image_dir', type=str, default="in_image", help="入力画像のディレクトリ")
    parser.add_argument('--in_video_dir', type=str, default="in_video", help="入力動画のディレクトリ")
    parser.add_argument('--in_audio_dir', type=str, default="in_audio", help="入力音声のディレクトリ")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))
    
    #----------------------------------
    # リクエスト処理
    #----------------------------------
    # 画像ファイル
    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(IMAGE_EXTENSIONS)] )
    for image_name in tqdm(image_names):
        files = {'file': (image_name, open(os.path.join(args.in_image_dir, image_name), "rb"), 'image/jpeg')}
        #files = {'file': open(os.path.join(args.in_image_dir, image_name), "rb")}
        try:
            api_responce = requests.post( "http://" + args.host + ":" + args.port + "/upload_file", files=files )
            api_responce = api_responce.json()
        except Exception as e:
            print( "Exception : ", e )
            time.sleep(1)
            continue

        if( api_responce["status"] == "ok" ):
            pass

        time.sleep(0.1)

    # 動画ファイル
    video_names = sorted( [f for f in os.listdir(args.in_video_dir) if f.endswith(VIDEO_EXTENSIONS)] )
    for video_name in tqdm(video_names):
        files = {'file': (video_name, open(os.path.join(args.in_video_dir, video_name), "rb"), 'video/mp4')}
        #files = {'file': open(os.path.join(args.in_video_dir, video_name), "rb")}
        try:
            api_responce = requests.post( "http://" + args.host + ":" + args.port + "/upload_file", files=files )
            api_responce = api_responce.json()
        except Exception as e:
            print( "Exception : ", e )
            time.sleep(1)
            continue

        if( api_responce["status"] == "ok" ):
            pass

        time.sleep(0.1)

    # 音声ファイル
    audio_names = sorted( [f for f in os.listdir(args.in_audio_dir) if f.endswith(AUDIO_EXTENSIONS)] )
    for audio_name in tqdm(audio_names):
        files = {'file': (audio_name, open(os.path.join(args.in_audio_dir, audio_name), "rb"), 'audio/mpeg')}
        #files = {'file': open(os.path.join(args.in_audio_dir, audio_name), "rb")}
        try:
            api_responce = requests.post( "http://" + args.host + ":" + args.port + "/upload_file", files=files )
            api_responce = api_responce.json()
        except Exception as e:
            print( "Exception : ", e )
            time.sleep(1)
            continue

        if( api_responce["status"] == "ok" ):
            pass

        time.sleep(0.1)
