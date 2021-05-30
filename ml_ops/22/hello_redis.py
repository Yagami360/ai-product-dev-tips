import os
import argparse
from PIL import Image
import redis

from redis_utils import set_image_pillow_redis, get_image_pillow_redis

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="localhost", help="redis サーバーのホスト名")
    parser.add_argument('--port', type=str, default="6379", help="redis サーバーのポート番号")
    parser.add_argument("--database_id", type=int, default=0, help="データベース番号")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    #-----------------------------
    # Redis サーバーに接続
    #-----------------------------
    redis_client = redis.Redis(host=args.host, port=args.port, db=args.database_id)

    #-----------------------------
    # 文字列型データの追加・取得・削除
    #-----------------------------
    # 文字列型データの追加
    redis_client.set('key1', 'value1')

    # 文字列型データの取得
    key1 = redis_client.get('key1')
    print( "key1 : ", key1 )

    # 文字列型データの削除
    result = redis_client.delete('key1')
    print( "result : ", result )

    key1 = redis_client.get('key1')
    print( "key1 : ", key1 )    # key がないので、None がかえる

    #-----------------------------
    # リスト型データ（キュー）の追加・取得・削除
    #-----------------------------    
    # rpush() : リストの末尾に値を追加
    redis_client.rpush('name', 'Tom')

    # rpop() : リストの末尾から値を pop
    name = redis_client.rpop('name')
    print( "[rpop] name : ", name)

    # lpush() : リストの先頭に値を追加
    redis_client.lpush('name', 'Taro')

    # lpop() : リストの先頭から値を pop
    name = redis_client.lpop('name')
    print( "[lpop] name : ", name)

    #-----------------------------
    # 画像データの追加・取得・削除
    #-----------------------------    
    img_pillow = Image.open( os.path.join("in_images", "2007_000032.jpg") )
    set_image_pillow_redis( redis_client, "image_key1", img_pillow )
    img_pillow_ = get_image_pillow_redis( redis_client, "image_key1" )
    img_pillow_.save( os.path.join("out_images", "2007_000032.jpg") )