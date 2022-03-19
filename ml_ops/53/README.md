# 【Sentry】Sentry を使用して　FastAPI を使用した Web-API のエラーを監視する（FastAPI + uvicorn + gunicorn + docker + docker-compose + Sentry での構成）

## ■ 方法

1. [Sentry のこ公式サイト](https://sentry.io/welcome/) にアクセスし、ユーザー登録を行い、Developer プランでプロジェクトを作成する。<br>

    > Developer プランは、無料で使用できる。ただしログデータ保持期間は 30 日のみで１人のみが使用できる

    この際の、プロジェクトのプラットホームは、Python を選択する
    <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/159109170-7974821b-b76a-41d1-9cb7-5325c4d8b178.png">


1. Python 選択後、以下のコード例が表示されるので、`${DSNの値}` の部分をコピーしておく<br>
    ```python
    import sentry_sdk
    sentry_sdk.init(
        "${DSNの値}",

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )
    ```

    > `${DSNの値}` は、作成したプロジェクトの「Setting」-> 「Projects」->「作成したプロジェクト名」->「Client Keys（DNS）」の画面からも確認できる。<br>
    > <img width="635" alt="image" src="https://user-images.githubusercontent.com/25688193/159112540-9f0df8a9-efab-4329-9903-286f5a93d9b1.png">


1. FastAPI を使用した Web-API の Dockerfile を作成する
    ```dockerfile
    #-----------------------------
    # Docker イメージのベースイメージ
    #-----------------------------
    FROM python:3.8-slim
    #FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

    #-----------------------------
    # 基本ライブラリのインストール
    #-----------------------------
    # インストール時のキー入力待ちをなくす環境変数
    ENV DEBIAN_FRONTEND noninteractive

    RUN set -x && apt-get update && apt-get install -y --no-install-recommends \
        sudo \
        git \
        curl \
        wget \
        bzip2 \
        ca-certificates \
        libx11-6 \
        python3-pip \
        # imageのサイズを小さくするためにキャッシュ削除
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

    RUN pip3 install --upgrade pip

    #-----------------------------
    # 環境変数
    #-----------------------------
    ENV LC_ALL=C.UTF-8
    ENV export LANG=C.UTF-8
    ENV PYTHONIOENCODING utf-8

    #-----------------------------
    # 追加ライブラリのインストール
    #-----------------------------
    RUN pip3 install fastapi
    RUN pip3 install uvicorn
    RUN pip3 install Gunicorn
    RUN pip3 install requests
    RUN pip3 install Pillow
    RUN pip3 install --upgrade sentry-sdk

    #-----------------------------
    # ソースコードの書き込み
    #-----------------------------
    #WORKDIR /api
    #COPY *.py /api/

    #-----------------------------
    # コンテナ起動後の作業ディレクトリ
    #-----------------------------
    WORKDIR /api
    ```
    ポイントは、以下の通り

    - `RUN pip3 install --upgrade sentry-sdk` で　Sentry の Python SDK をインストールしている

1. FastAPI を使用した Web-API のコードを作成する
    ```python
    import os
    import asyncio
    from datetime import datetime
    from time import sleep
    import logging
    from PIL import Image

    from fastapi import FastAPI
    from pydantic import BaseModel
    from typing import Any, Dict

    import sentry_sdk   # Sentry の Pyhton SDK

    import sys
    from utils.utils import conv_base64_to_pillow, conv_pillow_to_base64

    # logger
    if( os.path.exists(__name__ + '.log') ):
        os.remove(__name__ + '.log')
    logger = logging.getLogger(__name__)
    logger.setLevel(10)
    logger_fh = logging.FileHandler( __name__ + '.log')
    logger.addHandler(logger_fh)

    # sentry sdk 初期化
    sentry_sdk.init(
        "https://c3773729429b4e1a8b2c7d35424178f4@o1171856.ingest.sentry.io/6266790",   # DNS の値

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )

    #------------------------------
    # FastAPI の初期化
    #------------------------------
    app = FastAPI()
    print('[{}] time {} | 推論サーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
    logger.info('[{}] time {} | 推論サーバーを起動しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

    class ImageData(BaseModel):
        """
        画像データのリクエストボディ
        """
        image: Any
        image_height: Any
        image_width: Any

    #------------------------------
    # GET Method
    #------------------------------
    @app.get("/")
    def root():
        return 'Hello API Server!\n'

    @app.get("/health")
    def health():
        return {"health": "ok"}

    @app.get("/metadata")
    def metadata():
        return

    #------------------------------
    # POST Method
    #------------------------------
    @app.post("/predict")
    def predict(
        img_data: ImageData,        # リクエストボディ    
    ):
        print('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
        logger.info('[{}] time {} | リクエスト受付しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

        if(img_data.image_height >= 1024 or img_data.image_width >= 1024 ):
            # logger.error() で出力した ERROR レベルのログデータは Sentry で検出される 
            logger.error('[{}] time {} | image_height={}, image_width={}| 画像サイズの値が大き過ぎます'.format(__name__, f"{datetime.now():%H:%M:%S}", img_data.image_height, img_data.image_width))

            # 例外も Sentry で検出される
            raise Exception('too high image size exception.')
            """
            return {
                "status": "ng",
                "img_resized_base64" : None,
            }
            """
            
        # base64 -> Pillow への変換
        img_data.image = conv_base64_to_pillow(img_data.image)

        # resize
        img_resized_pillow = img_data.image.resize((img_data.image_width, img_data.image_height), Image.LANCZOS)

        # Pillow -> base64 への変換
        img_resized_base64 = conv_pillow_to_base64(img_resized_pillow)

        # レスポンスデータ設定
        print('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))
        logger.info('[{}] time {} | リクエスト処理完了しました'.format(__name__, f"{datetime.now():%H:%M:%S}"))

        return {
            "status": "ok",
            "img_resized_base64" : img_resized_base64,
        }
    ```

    ポイントは、以下の通り

    - `import sentry_sdk` で Sentry の Python SDK を import する

    - `sentry_sdk.init(...)` で Sentry の初期化を行う。このときの引数には、DNS の値を設定する

    - `logger.error()` で出力した ERROR レベルのログデータは Sentry で検出されるようになる（詳細は後述）

    - 同様に、`raise Exception(...)` で発生させた例外も Sentry で検出されるようになる（詳細は後述）

1. Web-API での推論処理を実行する
    ```sh
    # API 起動
    docker-compose -f docker-compose.yml stop
    docker-compose -f docker-compose.yml up -d
    sleep 5

    # リクエスト処理
    python3 request.py --host ${HOST} --port ${PORT} --in_images_dir ${IN_IMAGES_DIR} --out_images_dir ${OUT_IMAGES_DIR}
    ```

1. Sentry でエラー検出しているか確認する
    Sentry のプロジェクト画面右側にある「Issue」タブをクリックし、検出したエラー一覧を確認する

    <img width="700" alt="image" src="https://user-images.githubusercontent.com/25688193/159112270-b9514d2d-0fe0-4342-b066-715d0e69119b.png">


    - 例外エラーの詳細画面<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/159113071-4860b394-f887-4c57-b5d6-2fae6c2bcd7d.png"><br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/159112951-0fca7a9e-b98c-41af-b9ee-57146bd9e5b8.png"><br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/159112939-53a753da-0f03-4ed7-86f0-b09f98da61d7.png"><br>

        > 例外が発生した箇所のコードを確認できる

    - `logger.error()` で出力した ERROR レベルのログデータの詳細画面<br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/159113039-74a3d0ab-8e94-4541-ba97-334ee03161c1.png"><br>
        <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/159112999-c998c547-b37c-40e4-98a6-aaf75a5ec3dc.png"><br>

        > エラー発生前のログデータ等も確認できる

## ■ 参考サイト

- https://zenn.dev/a_ichi1/articles/f85f1b53b474cb
- https://qiita.com/Chanmoro/items/a9cbde57fd6c0926b5b4