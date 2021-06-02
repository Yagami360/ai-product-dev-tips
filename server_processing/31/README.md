# FastAPI + uvicorn での構成

## ■ 使用法

1. FastAPI をインストール
    ```sh
    $ pip install fastapi
    ```

1. uvicorn をインストール
    FastAPI の ASGI サーバーである uvicorn をインストールする
    ```sh
    $ pip install uvicorn
    ```

    > - WSGI [Web Server Gateway Interface]<br>
    >   Python で記述された Web アプリケーションと Web サーバー間との通信仕様を定めた通信プロトコル。この WSGI に従ったアプリケーションを動作させたサーバーを WSGI サーバーという<br>
    >   Flask や Django などのほとんどの Python 製 Web フレームワークは、この WSGI という通信プロトコルに則っている。<br>

    > - ASGI [Asynchronous Server Gateway Interface]<br>
    >    WSGI の拡張プ通信ロトコルで、非同期処理に対応した通信プロトコル。この ASGI に従ったアプリケーションを動作させたサーバーを ASGI サーバーという。<br>
    >    FastAPI は、ASGI に準拠した Web フレームワークになっている
    
1. FastAPI での api コードを作成する<br>
    例えば、以下のような FastAPI での api コード `app.py` を作成する

    - `uvicorn.run()` 不使用。サーバーを起動は、別途 `uvicorn` コマンドなどで実行する場合
        ```python
        # app1.py
        from fastapi import FastAPI

        app = FastAPI()

        @app.get("/")
        def hello_world():
            return 'Hello Flask-API Server!\n'
        ```

        - cf : Flask でのコード例（`app.run()` 不使用。サーバーを起動は、別途 `gunicorn` コマンドなどで実行する場合）<br>
            ```python
            import flask

            app = flask.Flask(__name__)

            @app.route('/')
            def hello_world():
                return 'Hello Flask-API Server!\n'
            ```

            > FastAPI は、Flask とよく似たコードになっている

    - `uvicorn.run()` 使用。python スクリプト内でサーバーを起動する場合<br>
        ```python
        # app2.py
        import argparse
        from fastapi import FastAPI
        import uvicorn

        app = FastAPI()

        @app.get("/")
        def hello_world():
            return 'Hello Flask-API Server!\n'

        if __name__ == "__main__":
            parser = argparse.ArgumentParser()
            parser.add_argument('--host', type=str, default="0.0.0.0", help="ホスト名（コンテナ名 or コンテナ ID）")
            parser.add_argument('--port', type=str, default="80", help="ポート番号")
            parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
            args = parser.parse_args()

            # FastAPI サーバー起動
            uvicorn.run(app, host=args.host, port=args.port)
        ```

        - cf : Flask でのコード例（`app.run()` を使用して python スクリプト内でサーバーを起動する場合）<br>
            ```python
            import argparse
            import flask

            app = flask.Flask(__name__)

            @app.route('/')
            def hello_world():
                return 'Hello Flask-API Server!\n'

            if __name__ == "__main__":
                parser = argparse.ArgumentParser()
                parser.add_argument('--host', type=str, default="0.0.0.0", help="ホスト名（コンテナ名 or コンテナ ID）")
                parser.add_argument('--port', type=str, default="5000", help="ポート番号")
                parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
                args = parser.parse_args()

                # Flask の起動
                app.run(host=args.host, port=args.port)
            ```

1. FastAPI サーバーを起動する<br>
    - `uvicorn.run()` 不使用。サーバーを起動は、別途 `uvicorn` コマンドなどで実行する場合<br>
        `uvicorn` コマンドを使用して API サーバーを起動する
        ```sh
        $ uvicorn app:app --reload --host ${HOST} --port ${PORT}
        ```
        - `app:app` : APIコードのファイル名:FastAPI()のインスタンス名

    - `uvicorn.run()` 使用。python スクリプト内でサーバーを起動する場合<br>
        ```sh
        $ python app2.py --host ${HOST} --port ${PORT}
        ```

1. リクエスト処理を送信する<br>
    `curl` コマンドなどで、起動した API サーバーのエンドポイントにアクセスし、リクエスト処理を行う。    
    ```sh
    $ curl http://${HOST}:${PORT}
    ```

## ■ FastAPI での処理例

### ◎ GET method

### ◎ POST method


## ■ 参考サイト
- https://qiita.com/bee2/items/75d9c0d7ba20e7a4a0e9
- https://qiita.com/BrainVader/items/ca3b0c6f828b4e64d13f