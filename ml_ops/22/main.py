import os
import sys
import argparse

import redis

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="0.0.0.0", help="redis サーバーのホスト名")
    parser.add_argument('--port', type=str, default="80", help="redis サーバーのポート番号")
    parser.add_argument("--database_id", type=int, default=0, help="データベース番号")
    parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
    args = parser.parse_args()
    if( args.debug ):
        for key, value in vars(args).items():
            print('%s: %s' % (str(key), str(value)))

    # Redis サーバーに接続
    redis = redis.Redis(host=args.host, port=args.port, db=args.database_id)

    