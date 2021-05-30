# coding=utf-8
import os
import sys
import argparse
import json
from PIL import Image
from tqdm import tqdm 
import time, datetime
import requests

# Clloud Pub/Sub
from google.cloud import pubsub_v1

# グローバル変数
IMG_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif',
    '.JPG', '.JPEG', '.PNG', '.PPM', '.BMP', '.PGM', '.TIF',
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument('--host', type=str, default="localhost", help="API サーバーのホスト名（コンテナ名 or コンテナ ID）")
    #parser.add_argument('--port', type=str, default="80", help="API サーバーのポート番号")
    parser.add_argument("--project_id", default="my-project2-303004", help="GCP のプロジェクトID")
    parser.add_argument("--topic_name", type=str, default="topic-sample", help="Pub/Sub のトピック名")
    parser.add_argument("--credentials_file_path", type=str, default="", help="Pub/Sub のjson鍵のファイルパス")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))
    
    """
    api_server_url = "http://" + args.host + ":" + args.port + "/api_server"
    if( args.debug ):
        print( "api_server_url : ", api_server_url )
    """
    
    # publisher のインスタンス作成
    publisher = pubsub_v1.publisher.Client.from_service_account_file(args.credentials_file_path)
    topic_path = publisher.topic_path(args.project_id, args.topic_name)

    #----------------------------------
    # リクエスト処理
    #----------------------------------
    """
    request_msg = { 'test_value' : 0 }
    request_msg = json.dumps(request_msg)
    try:
        api_responce = requests.post( api_server_url, json=request_msg )
        api_responce = api_responce.json()
        if( args.debug ):
            print( "api_responce : ", api_responce )

    except Exception as e:
        print( "通信失敗 [API server]" )
        print( "Exception : ", e )
        exit()

    print( "api_responce[status] : ", api_responce["status"] )
    """

    # メッセージの設定
    request_msg = { 'test_value' : 0 }
    request_msg = json.dumps(request_msg)

    # トピックにメッセージを publish (push) する
    future = publisher.publish(topic_path, data=request_msg)
    print("return ", future.result())
