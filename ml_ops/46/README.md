# FastAPI を使用した Web-API にファイルをアップロードする

FastAPI にファイルをアップロードすることで、動画ファイルや音声ファイルなどの容量の大きいファイルを API にリクエストすることができる

## ■ 方法

1. FastAPI のコードでファイルをアップロードするエンドポイントを実装する<br>
    FastAPI の `UploadFile` オブジェクトを使用して、ファイルをアップロードするためのエンドポイント `upload_file(...)` を実装する。

    ```python
    # 重要な部分のみ抜粋
    from fastapi import FastAPI
    from fastapi import UploadFile, File, HTTPException
    ...

    @app.post("/upload_file")
    async def upload_file(file: UploadFile = File(...)):
        start_time = time.time()
        logger.info("{} {} {} {} file_name={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "START", file.filename))
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
        logger.info("{} {} {} {} elapsed_time [ms]={:.5f} file_name={}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "INFO", sys._getframe().f_code.co_name, "END", elapsed_time, file.filename))
        return responce
    ```

    > FastAPI の `UploadFile` `File` を使用するには、別途 `python-multipart` をインストールする必要がある

    > アップロードしたファイルを `shutil.copyfileobj` でディスクに書き込んでいる。今回の API では行っていないが、書き込んだファイルを再度読み込みことで、リクエストされたファイルへの操作が可能になる。

1. WebAPI の Dockerfile を作成する
1. docker-compose を作成する

1. リクエスト処理する<br>
    1. `curl` コマンドを使用する場合<br>
        `curl` コマンドの `-F` オプションでアップロードするファイル名を指定し、Web-API にリクエスト処理する<br>
        - 画像データ `*.jpg` の場合
            ```sh
            curl -X POST "http://${HOST}:${PORT}/upload_file" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "${ENDPOINT_FUNCTION_ARGS_NAME}=@${FILE_PATH};type=image/jpeg"
            ```
            - `${ENDPOINT_FUNCTION_ARGS_NAME}` : エンドポイントの関数で指定された `UploadFile` オブジェクトの引数名。今回の例では、`async def _upload_file(file: UploadFile = File(...)):` がエンドポイントになっているが、この関数の `UploadFile` オブジェクトの引数名 `file` がこれに相当する

        - 動画データ `*.mp4` の場合
            ```sh
            curl -X POST "http://${HOST}:${PORT}/upload_file" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "${ENDPOINT_FUNCTION_ARGS_NAME}=@${FILE_PATH};type=video/mp4"
            ```

        - 音声データ `*.mp3` の場合
            ```sh
            curl -X POST "http://${HOST}:${PORT}/upload_file" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "${ENDPOINT_FUNCTION_ARGS_NAME}=@${FILE_PATH};type=audio/mpeg"
            ```

    1. `request` モジュールを使用する場合<br>
        `requests.post(...)` を使用して、FastAPI にファイルをアップロードすることもできる

        - 画像データ `*.jpg` の場合
            ```python
            # 抜粋コード
            files = {'file': (image_name, open(os.path.join(args.in_image_dir, image_name), "rb"), 'image/jpeg')}
            api_responce = requests.post( "http://" + args.host + ":" + args.port + "/upload_file", files=files )
            ```
            > `requests.post(...)` の `files` 引数で指定している名前 `'file'` は、エンドポイントの関数で指定された `UploadFile` オブジェクトの引数名に対応。今回の例では、`async def _upload_file(file: UploadFile = File(...)):` がエンドポイントになっているが、この関数の `UploadFile` オブジェクトの引数名 `file` がこれに相当する

        - 動画データ `*.mp4` の場合
            ```python
            # 抜粋コード
            files = {'file': (video_name, open(os.path.join(args.in_video_dir, video_name), "rb"), 'video/mp4')}
            api_responce = requests.post( "http://" + args.host + ":" + args.port + "/upload_file", files=files )
            ```

        - 音声データ `*.mp3` の場合
            ```python
            # 抜粋コード
            files = {'file': (audio_name, open(os.path.join(args.in_audio_dir, audio_name), "rb"), 'audio/mpeg')}
            #files = {'file': open(os.path.join(args.in_audio_dir, audio_name), "rb")}
            api_responce = requests.post( "http://" + args.host + ":" + args.port + "/upload_file", files=files )
            ```

## ■ 参考サイト

- https://www.ravness.com/posts/fileuploadwithfastapi
- https://fastapi.tiangolo.com/tutorial/request-files/


