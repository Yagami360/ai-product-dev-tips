# coding=utf-8
import os
import sys
import argparse
import json
from PIL import Image
from tqdm import tqdm 
import requests

# 自作モジュール
from api.utils.utils import conv_base64_to_pillow, conv_pillow_to_base64

# グローバル変数
IMG_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif',
    '.JPG', '.JPEG', '.PNG', '.PPM', '.BMP', '.PGM', '.TIF',
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="localhost", help="APIサーバーのホスト名（コンテナ名 or コンテナ ID）")
    parser.add_argument('--port', type=str, default="5001", help="APIサーバーのポート番号")
    parser.add_argument('--timeout', type=int, default=60, help="タイムアウト時間 [s]")
    parser.add_argument('--in_images_dir', type=str, default="in_images", help="")
    parser.add_argument('--out_images_dir', type=str, default="out_images", help="")
    parser.add_argument('--image_height', type=int, default=256, help="")
    parser.add_argument('--image_width', type=int, default=192, help="")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    if not os.path.isdir(args.out_images_dir):
        os.mkdir(args.out_images_dir)
    
    image_names = sorted( [f for f in os.listdir(args.in_images_dir) if f.endswith(IMG_EXTENSIONS)] )
    for img_name in tqdm(image_names):
        #----------------------------------
        # リクエスト送信データの設定
        #----------------------------------
        img_pillow = Image.open( os.path.join(args.in_images_dir, img_name) )
        img_base64 = conv_pillow_to_base64(img_pillow)

        #----------------------------------
        # リクエスト処理
        #----------------------------------
        try:
            api_responce = requests.post(
              "http://" + args.host + ":" + args.port + "/predict",
              json={
                'image': img_base64,
                "image_height": args.image_height,
                "image_width": args.image_width
              },
              timeout=(10.0, args.timeout)
            )
            api_responce = api_responce.json()
        except Exception as e:
            print( "通信失敗" )
            print( "Exception : ", e )
            continue
        finally:
            args.image_height = 2 * args.image_height
            args.image_width = 2 * args.image_width

        #----------------------------------
        # ファイルに保存
        #----------------------------------
        if( api_responce["status"] == "ok" ):
            img_resized_base64 = api_responce["img_resized_base64"]
            img_resized_pillow = conv_base64_to_pillow(img_resized_base64)
            img_resized_pillow.save( os.path.join( args.out_images_dir, img_name.split(".")[0] + ".png" ) )

