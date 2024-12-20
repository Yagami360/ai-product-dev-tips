# Redis を Python スクリプトで使用する


## ■ 使用法

1. Redis サーバーの設定
    1. Redis をインストールする
        - Mac OS の場合
            ```sh
            $ brew install redis
            ```

        - Ubuntu の場合
            ```sh
            $ sudo apt install redis-server
            ```

    1. Redis サーバーを起動する
        ```sh
        $ redis-server
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

## ■ Redis での処理例

- Redis サーバーへの接続
    ```python
    import redis

    # Redis サーバーに接続
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    ```

- 文字列型データの追加・取得・削除
    ```python
    import redis

    # Redis サーバーに接続
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    # 文字列型データの追加
    redis_client.set('key1', 'value1')

    # 文字列型データの取得
    key1 = redis_client.get('key1')
    print( "key1 : ", key1 )

    # 文字列型データの削除
    result = redis_client.delete('key1')
    print( "result : ", result )
    ```

- リスト型データ（キュー）の追加・取得・削除<br>
    ```python
    import redis

    # Redis サーバーに接続
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    # rpush() : リストの末尾に値を追加
    redis_client.rpush('name', 'Tom')

    # rpop() : リストの末尾から値を pop
    name = redis_client.rpop('name')
    print(name)

    # lpush() : リストの先頭に値を追加
    redis_client.lpush('name', 'Taro')

    # lpop() : リストの先頭から値を pop
    name = redis_client.lpop('name')
    print(name)
    ```

- 画像データの追加・取得・削除<br>
    Redis に画像データを追加・取得・削除したい場合は、Pillow での画像データを base64 形式に変換した上で、文字列型データの追加・取得・削除と同様の方法で追加・取得・削除すればよい

    ```python
    import os
    import io
    import base64
    from PIL import Image
    import redis

    # Redis サーバーに接続
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    # Pillow 
    img_pillow = Image.open( os.path.join("in_images", "2007_000032.jpg") )

    # Pillow データを base64 形式に変換
    bytes_io = io.BytesIO()
    img_pillow.save(bytes_io, format=img_pillow.format)
    img_base64_enc = base64.b64encode(bytes_io.getvalue())

    # base64 形式での画像データを追加
    redis_client.set("image", img_base64_enc)

    # base64 形式での画像データを取得
    img_base64_redis = redis_client.get("image")
    img_base64_dec = base64.b64decode(img_base64_redis)
    io_bytes = io.BytesIO(img_base64_dec)
    img_pillow_dec = Image.open(io_bytes)
    img_pillow_dec.save( os.path.join("out_images", "2007_000032.jpg") )
    ```    

## ■ 参考サイト
- https://weblabo.oscasierra.net/python/python-redis-py-1.html