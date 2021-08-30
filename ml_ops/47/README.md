# FastAPI を使用した Web-API に複数ファイルを同時にアップロードする

FastAPI にファイルをアップロードすることで、動画ファイルや音声ファイルなどの容量の大きいファイルを API にリクエストすることができる

## ■ 方法

1. FastAPI のコードでファイルをアップロードするエンドポイントを実装する<br>
    FastAPI の `UploadFile` オブジェクトの `List` 型を使用して、ファイルをアップロードするためのエンドポイント `upload_files(...)` を実装する。

    ```python
    # 重要な部分のみ抜粋
    from typing import List
    from fastapi import FastAPI
    from fastapi import UploadFile, File, HTTPException
    ...
    @app.post("/upload_files")
    async def upload_files(files: List[UploadFile] = File(...)):
        start_time = time.time()
        logger.info("{} {} {} {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START"))
        for file in files:
            try:
                with open(os.path.join(FastAPIServerConfig.upload_dir, file.filename),'wb+') as buffer:
                    shutil.copyfileobj(file.file, buffer)
                responce = {
                    "status": "ok",
                    "file_name": file.filename,
                    "file_path": os.path.join(FastAPIServerConfig.upload_dir,file.filename),
                }
            except Exception as e:
                responce = {
                    "status": "ng",
                    "file_name": None,
                    "file_path": None,
                }
            finally:
                file.file.close()

        elapsed_time = 1000 * (time.time() - start_time)
        logger.info("{} {} {} {} elapsed_time [ms]={:.5f}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", elapsed_time))
        return responce
    ```

    > FastAPI の `UploadFile` `File` を使用するには、別途 `python-multipart` をインストールする必要がある

    > アップロードしたファイルを `shutil.copyfileobj` でディスクに書き込んでいる。今回の API では行っていないが、書き込んだファイルを再度読み込みことで、リクエストされたファイルへの操作が可能になる。

1. WebAPI の Dockerfile を作成する
1. docker-compose を作成する

1. リクエスト処理する<br>
    1. `curl` コマンドを使用する場合<br>
        `curl` コマンドの `-F` オプションを複数使用することで、複数のファイルを Web-API にアップロードできる<br>

        ```sh
        $ curl -X POST "http://${HOST}:${PORT}/upload_files" \
            -H "accept: application/json" -H "Content-Type: multipart/form-data" \
            -F "files=@${IN_IMAGE_DIR}/1.jpg;type=image/jpeg" \
            -F "files=@${IN_VIDEO_DIR}/1.mp4;type=video/mp4" \
            -F "files=@${IN_AUDIO_DIR}/1.mp3;type=audio/mpeg"
        ```
        > `-F` オプションで指定している `"files"` は、エンドポイントの関数で指定された `UploadFile` オブジェクトのリストの引数名に対応。今回の例では、`async def upload_files(files: List[UploadFile] = File(...)):` がエンドポイントになっているが、この関数の `UploadFile` オブジェクトのリストの引数名 `files` がこれに相当する


    1. `request` モジュールを使用する場合<br>
        `requests.post(...)` を使用して、FastAPI に複数のファイルを同時にアップロードすることもできる
        ```python
        # 抜粋コード
        files = {
            ( 'files', (image_name, open(os.path.join(args.in_image_dir, image_name), "rb"), 'image/jpeg') ),
            ( 'files', (video_name, open(os.path.join(args.in_video_dir, video_name), "rb"), 'video/mp4') ),
            ( 'files', (audio_name, open(os.path.join(args.in_audio_dir, audio_name), "rb"), 'audio/mpeg') ),
        }
        api_responce = requests.post( "http://" + args.host + ":" + args.port + "/upload_files", files=files )
        api_responce = api_responce.json()
        ```

        > `{ ("xxx",(xxx)), ("xxx",(xxx)), ("xxx",(xxx))}` の形式で `files` 引数を設定することで、複数のファイルを同時にアップロードできる

        > `requests.post(...)` の `files` 引数で指定している名前 `'files'` は、エンドポイントの関数で指定された `UploadFile` オブジェクトのリスト引数名に対応。今回の例では、`async def upload_files(files: List[UploadFile] = File(...)):` がエンドポイントになっているが、この関数の `UploadFile` オブジェクトのリストの引数名 `files` がこれに相当する

## ■ 参考サイト
- https://fastapi.tiangolo.com/tutorial/request-files/


