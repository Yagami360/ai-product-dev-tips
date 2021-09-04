import os
import sys
import argparse
import json
from PIL import Image
from tqdm import tqdm 
import requests
import time

# グローバル変数
VIDEO_EXTENSIONS = (
    '.mp4',
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="localhost", help="API サーバーのホスト名（コンテナ名 or コンテナ ID）")
    parser.add_argument('--port', type=str, default="5000", help="API サーバーのポート番号")
    parser.add_argument('--in_video_dir', type=str, default="in_video", help="入力動画のディレクトリ")
    parser.add_argument('--out_video_dir', type=str, default="out_video", help="出力ディレクトリ")
    parser.add_argument('--n_pollings', type=int, default=100, help="ポーリング回数")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))
    
    if not os.path.isdir(args.out_video_dir):
        os.mkdir(args.out_video_dir)

    #----------------------------------
    # ジョブ開始
    #----------------------------------
    video_names = sorted( [f for f in os.listdir(args.in_video_dir) if f.endswith(VIDEO_EXTENSIONS)] )
    job_ids = []
    for video_name in tqdm(video_names):
        files = {'file': (video_name, open(os.path.join(args.in_video_dir, video_name), "rb"), 'video/mp4')}
        try:
            api_responce = requests.post( "http://" + args.host + ":" + args.port + "/predict", files=files )
            api_responce = api_responce.json()
        except Exception as e:
            print( "Exception : ", e )
            time.sleep(1)
            continue

        job_id = api_responce["job_id"]
        job_status = api_responce["job_status"]
        print( "video_name={}, job_id={}, job_status={}".format(video_name, job_id, job_status) )
        job_ids.append(job_id)

        time.sleep(0.1)

    #----------------------------------
    # job の確認
    #----------------------------------
    for n_polling in tqdm(range(args.n_pollings)):
        if(len(job_ids)==0):
            break
        for i,job_id in enumerate(job_ids):
            job_data = requests.get( "http://" + args.host + ":" + args.port + "/get/" + job_id ).json()
            if( job_data["status"] == "ok" ):
                pass

        time.sleep(1)
