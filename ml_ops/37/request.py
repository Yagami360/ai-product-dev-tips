import os
import sys
import argparse
import json
from PIL import Image
from tqdm import tqdm 
import requests
import time

# 自作モジュール
from utils.img_utils import conv_base64_to_pillow, conv_pillow_to_base64

# グローバル変数
IMG_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif',
    '.JPG', '.JPEG', '.PNG', '.PPM', '.BMP', '.PGM', '.TIF',
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="localhost", help="API サーバーのホスト名（コンテナ名 or コンテナ ID）")
    parser.add_argument('--port', type=str, default="5000", help="API サーバーのポート番号")
    parser.add_argument('--in_images_dir', type=str, default="in_images", help="入力画像のディレクトリ")
    parser.add_argument('--out_images_dir', type=str, default="out_images", help="出力ディレクトリ")
    parser.add_argument('--n_pollings', type=int, default=100, help="ポーリング回数")
    parser.add_argument('--sleep', type=int, default=0.1, help="ポーリング間隔[sec単位]")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))
    
    if not os.path.isdir(args.out_images_dir):
        os.mkdir(args.out_images_dir)

    #----------------------------------
    # ヘルスチェック
    #----------------------------------
    health = requests.get( "http://" + args.host + ":" + args.port + "/health" ).json()
    print( "health : ", health )

    #----------------------------------
    # metadata 取得
    #----------------------------------
    metadata = requests.get( "http://" + args.host + ":" + args.port + "/metadata" ).json()
    print( "metadata : ", metadata )

    #----------------------------------
    # predict
    #----------------------------------
    image_names = sorted( [f for f in os.listdir(args.in_images_dir) if f.endswith(IMG_EXTENSIONS)] )
    job_ids = []
    for img_name in tqdm(image_names):
        # リクエスト送信データの設定
        img_pillow = Image.open( os.path.join(args.in_images_dir, img_name) )
        img_base64 = conv_pillow_to_base64(img_pillow)

        # リクエスト処理
        api_msg = {'image': img_base64}
        #api_msg = json.dumps(api_msg)  # Fast API では、json.dump() で dict 型データを JSON 形式に変換する必要はない
        try:
            api_responce = requests.post( "http://" + args.host + ":" + args.port + "/predict", json=api_msg )
            api_responce = api_responce.json()
        except Exception as e:
            print( "Exception : ", e )
            time.sleep(1)
            continue

        print( "api_responce : ", api_responce )

    #----------------------------------
    # ポーリング
    #----------------------------------
    for i in range(args.n_pollings):
        # リクエスト処理
        log_all_data = requests.get( "http://" + args.host + ":" + args.port + "/get_log_all" ).json()
        print( "log_all_data", log_all_data )
        time.sleep(args.sleep)
        
    #img_out_pillow = conv_base64_to_pillow(api_responce["img_base64"])
    #img_out_pillow.save(os.path.join(args.out_images_dir,img_name))
            
