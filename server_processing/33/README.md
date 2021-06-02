# FastAPI + uvicorn + gunicorn + docker を用いた Web-API の構築

## ■ 使用法
    
1. FastAPI での api コードを作成する<br>
    例えば、以下のような FastAPI での api コード `app.py` を作成する

    > gunicorn 連携時は、`uvicorn.run()` は使用せず、サーバーの起動は別途 `gunicorn` コマンドで実行する必要があることに注意

    ```python
    # app.py
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/")
    def hello_world():
        return 'Hello Flask-API Server!\n'
    ```

1. FastAPI サーバーの Dockerfile を作成する<br>
    ```dockerfile

    ```

1. docker-compose を作成する<br>
    docker-compose を使って、API サーバーの起動や停止を行う場合は、`docker-compose.yml` も作成する
    ```yml
    version: '2.3'

    services:
    fast_api_server:
        container_name: fast-api-container
        image: fast-api-image
        build:
            context: "api/"
            dockerfile: Dockerfile
        volumes:
            - ${PWD}/api:/api
        ports:
            - "5000:5000"
        tty: true
        environment:
            TZ: "Asia/Tokyo"
            LC_ALL: C.UTF-8
            LANG: C.UTF-8
        command: bash -c "gunicorn app:app --bind 0.0.0.0:5000 -w 1 -k uvicorn.workers.UvicornWorker --reload"
    ```

1. API サーバーを起動する
    ```sh
    $ docker-compose -f docker-compose.yml stop
    $ docker-compose -f docker-compose.yml up -d
    ```

1. リクエスト処理を送信する<br>
    `curl` コマンドなどで、起動した API サーバーのエンドポイントにアクセスし、リクエスト処理を行う。    
    ```sh
    $ curl http://${HOST}:${PORT}
    ```



## ■ 参考サイト

- https://qiita.com/uezo/items/847e1911ac486f5a89c4