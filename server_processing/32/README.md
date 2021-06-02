# FastAPI + uvicorn + gunicorn での構成（本番環境想定時）

## ■ 使用法
    
uvicorn のマニュアルには、以下の記載がある。

> For production deployments we recommend using gunicorn with the uvicorn worker class.

これは具体的には、uvicorn 自体でマルチプロセスの仕組みは持っているが、プロセスを監視して落ちたら再起動するといったような本番環境を想定した仕組みが無いことを意味している。

そのため、本番環境を想定する場合は、FastAPI + uvicorn + gunicorn での構成にする必要がる。

1. FastAPI をインストール
    ```sh
    $ pip install fastapi
    ```

1. uvicorn をインストール
    FastAPI の ASGI サーバーである uvicorn をインストールする
    ```sh
    $ pip install uvicorn
    ```

1. gunicorn をインストール
    WSGI サーバーである gunicorn をインストールする
    ```sh
    $ pip install Gunicorn
    ```

    > - WSGI [Web Server Gateway Interface]<br>
    >   Python で記述された Web アプリケーションと Web サーバー間との通信仕様を定めた通信プロトコル。この WSGI に従ったアプリケーションを動作させたサーバーを WSGI サーバーという<br>
    >   Flask や Django などのほとんどの Python 製 Web フレームワークは、この WSGI という通信プロトコルに則っている。<br>

    > - ASGI [Asynchronous Server Gateway Interface]<br>
    >    WSGI の拡張プ通信ロトコルで、非同期処理に対応した通信プロトコル。この ASGI に従ったアプリケーションを動作させたサーバーを ASGI サーバーという。<br>
    >    FastAPI は、ASGI に準拠した Web フレームワークになっている

1. FastAPI での api コードを作成する<br>
    例えば、以下のような FastAPI での api コード `app.py` を作成する

    > `uvicorn.run()` は使用せず、サーバーの起動は別途 `gunicorn` コマンドで実行する必要があることに注意

    ```python
    # app.py
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/")
    def hello_world():
        return 'Hello Flask-API Server!\n'
    ```

1. FastAPI サーバーを起動する<br>
    `gunicorn` コマンドを使用して API サーバーを起動する
    ```sh
    $ gunicorn app:app --bind ${HOST}:${PORT} -w ${N_WORKERS} -k uvicorn.workers.UvicornWorker --reload
    ```
    - `app:app` : APIコードのファイル名:FastAPI()のインスタンス名
    - `-w` : プロセス数
    - `-k` : uvicorn を ASGI サーバーにする場合は、`uvicorn.workers.UvicornWorker` を指定

1. リクエスト処理を送信する<br>
    `curl` コマンドなどで、起動した API サーバーのエンドポイントにアクセスし、リクエスト処理を行う。    
    ```sh
    $ curl http://${HOST}:${PORT}
    ```


## ■ 参考サイト

- https://qiita.com/uezo/items/847e1911ac486f5a89c4