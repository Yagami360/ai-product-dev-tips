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
    parser.add_argument('--in_image_dir', type=str, default="sample_n5", help="入力人物画像のディレクトリ")
    parser.add_argument('--results_dir', type=str, default="results", help="出力人物パース画像を保存するディレクトリ")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    if not os.path.isdir(args.results_dir):
        os.mkdir(args.results_dir)
    
    graphonomy_server_url = "http://" + args.host + ":" + args.port + "/predict"
    if( args.debug ):
        print( "graphonomy_server_url : ", graphonomy_server_url )

    image_names = sorted( [f for f in os.listdir(args.in_image_dir) if f.endswith(IMG_EXTENSIONS)] )
    for img_name in tqdm(image_names):
        #----------------------------------
        # リクエスト送信データの設定
        #----------------------------------
        pose_img_pillow = Image.open( os.path.join(args.in_image_dir, img_name) )
        pose_img_base64 = conv_pillow_to_base64(pose_img_pillow)

        #----------------------------------
        # リクエスト処理
        #----------------------------------
        graphonomy_msg = {'pose_img_base64': pose_img_base64 }
        try:
            graphonomy_responce = requests.post( graphonomy_server_url, json=graphonomy_msg, timeout=(10.0, 60.0))
            graphonomy_responce = graphonomy_responce.json()
        except Exception as e:
            print( "通信失敗 [Graphonomy]" )
            print( "Exception : ", e )
            continue

        #----------------------------------
        # ファイルに保存
        #----------------------------------
        pose_parse_img_base64 = graphonomy_responce["pose_parse_img_base64"]
        pose_parse_img_RGB_base64 = graphonomy_responce["pose_parse_img_RGB_base64"]

        pose_parse_img_pillow = conv_base64_to_pillow(pose_parse_img_base64)
        pose_parse_img_RGB_pillow = conv_base64_to_pillow(pose_parse_img_RGB_base64)

        pose_parse_img_pillow.save( os.path.join( args.results_dir, img_name.split(".")[0] + ".png" ) )
        pose_parse_img_RGB_pillow.save( os.path.join( args.results_dir, img_name.split(".")[0] + "_vis.png" ) )
