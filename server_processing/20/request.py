# coding=utf-8
import os
import sys
import argparse
import json
from PIL import Image
from tqdm import tqdm 
import requests

# グローバル変数
IMG_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif',
    '.JPG', '.JPEG', '.PNG', '.PPM', '.BMP', '.PGM', '.TIF',
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="localhost", help="API サーバーのホスト名（コンテナ名 or コンテナ ID）")
    parser.add_argument('--port', type=str, default="80", help="API サーバーのポート番号")
    parser.add_argument('--use_https', action='store_true', help="https使用有無")
    parser.add_argument('--verify_ssl', action='store_true', help="ssl認証のverify処理有無")
    parser.add_argument('--crt_file_path', type=str, default="api/open_ssl/server.crt", help="SSLサーバー証明書（*.crt）のパス")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))
    
    if(args.use_https):
        api_server_url = "https://" + args.host + ":" + args.port + "/api_server"
    else:
        api_server_url = "http://" + args.host + ":" + args.port + "/api_server"        

    if( args.debug ):
        print( "api_server_url : ", api_server_url )

    #----------------------------------
    # リクエスト処理
    #----------------------------------
    request_msg = { 'test_value' : 0 }
    request_msg = json.dumps(request_msg)
    try:
        if(args.use_https):
            if(args.verify_ssl):
                api_responce = requests.post( api_server_url, json=request_msg, verify=args.crt_file_path )
            else:
                api_responce = requests.post( api_server_url, json=request_msg, verify=False )
        else:
            api_responce = requests.post( api_server_url, json=request_msg )

        api_responce = api_responce.json()
        if( args.debug ):
            print( "api_responce : ", api_responce )

    except Exception as e:
        print( "通信失敗 [API server]" )
        print( "Exception : ", e )
        exit()

    print( "api_responce[status] : ", api_responce["status"] )
