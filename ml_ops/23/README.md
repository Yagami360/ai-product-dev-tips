# docker + Redis + Python での Redis の構成

<!--
Redis サーバーを docker コンテナ上で実行することで、Redis サーバーの起動処理と Python での Redis 処理を別プロセスにわけて
-->

## ■ 使用法

1. Redis サーバーの設定
    1. Redis サーバーの docker-compose を作成<br>
        Redis サーバーの dockerfile は作成せず、`redis:latest` の docker イメージを直接使用する
        ```yml
        version: '2.3'
        services:
          redis_server:
            container_name: redis_container
            image: redis:latest
            ports:
              - "6379:6379"
            tty: true
            environment:
              TZ: "Asia/Tokyo"
              LC_ALL: C.UTF-8
              LANG: C.UTF-8
            command: bash -c "redis-server"
        ```

    1. Redis サーバーを起動する
        ```sh
        $ docker-compose -f docker-compose.yml stop
        $ docker-compose -f docker-compose.yml up -d
        ```

1. Redis の Python スクリプトの設定
    1. Redis の Python API `redis-py` をインストールする
        ```sh
        $ pip install redis
        ```

    1. Redis の Python スクリプトを作成
        例えば、以下のような Redis の Python API を利用した Python スクリプトを作成する
        ```python
        # hello_redis.py
        import os
        import argparse
        import redis

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
        ```

    1. Redis の Python スクリプトを実行<br>
        Redis サーバー起動中に、上記で作成した Python スクリプトを実行する。
        ```sh
        $ python hello_redis.py
        ```

