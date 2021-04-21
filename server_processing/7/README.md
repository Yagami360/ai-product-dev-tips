# 【GCP】Cloud Functions を利用したサーバーレス Web-API

- Cloud Functions 導入のメリット
    - サーバーのオートスケーリング、ロードバランサーなどを自動的に行ってくれる。

- Cloud Functions 導入のデメリット
    - サーバレスなので、ファイルへの IO処理をサーバー上ではなく GCS で行う必要がある。
        - これにより、サーバー上で動作していたコードの IO 処理部分が Cloud Function では動作しなくなるケースが多々ある。
    - デプロイ処理に時間がかかり、デバッグ作業が非効率になる
        - [ローカルでの関数の実行](https://firebase.google.com/docs/functions/local-emulator?hl=ja) の方法で解決可能？
    - GPU が必要な処理（PyTorch）を実行できない

## ■ 実現方法
Cloud Functions は、以下の手順で利用できる
1. Cloud Functions 用のコードの作成
1. Cloud Functions の作成（＝作成したコードのデプロイ処理）
1. Cloud Functions の動作テスト

### 1. Cloud Functions 用のコードの作成
1. Cloud Function 上で実行するコード（APIコード）を作成する。
    例えば、Flask などを使用して、Cloud Function 上で実行するコード（APIコード） `main.py` を作成する。

    このとき、Cloud Function を利用する場合の Flask での API コードの形式は、以下のようなエントリーポイント関数で引数をとらない一般的な形式ではなく、引数をとる形式にする変更する必要があることに注意

    - Cloud Function 以外での Flask コードの一般的な形式
        ```python
        import flask
        # エントリーポイントの関数 responce() の引数は取らない
        @app.route('/api_server', methods=['POST'])
        def responce():
            if( flask.request.headers["User-Agent"].split("/")[0] in "python-requests" ):
                json_data = json.loads(flask.request.json)
            else:
                json_data = flask.request.get_json()
            ...
        ```

    - Cloud Function で動作する Flask コードの一般的な形式
        ```python
        import flask
        # エントリーポイントの関数 responce() の引数に request が入力される
        @app.route('/api_server', methods=['POST'])
        def responce(request):
            if( flask.request.headers["User-Agent"].split("/")[0] in "python-requests" ):
                json_data = json.loads(flask.request.json)
            else:
                json_data = flask.request.get_json()
            ...
        ```

1. `requirements.txt` を作成。
    外部ライブラリを使用している場合は、それらのライブラリを `requirements.txt` に記載する必要がある。
    Cloud Function デプロイ時に、この `requirements.txt` に従って外部ライブラリが Cloud Function 上にインストールされる。


### 2. Cloud Functions の作成（＝作成したコードのデプロイ処理）

#### ☆ GUI 使用時
省略

#### ☆ GUI 非使用時（コマンド使用）
Cloud Functions 作成後、GUI のブラウザエディターでのコードを作成することもできるが、このエディターは使いにくいので、VSCode などのエディタでコード作成後、`gcloud` のコマンドを使用して Cloud Functions 作成＆デプロイ処理を行う流れにしたほうが使いやすい。

Cloud Functions の作成からデプロイ処理までを行うコマンドには、以下のコマンドがある。

- Cloud Functions の作成＆デプロイ処理
    ```sh
    $ gcloud functions deploy ${FUNCTION_NAME} \
        --region asia-northeast1 \
        --memory 256MB \
        --source . \
        --entry-point ${ENTORY_NAME} \
        --runtime python37 \
        --trigger-http
    ```
    - `${FUNCTION_NAME}` : 作成する Cloud Functions の名前
    - `--region` : Cloud Functions を作成するリージョン
    - `--memory` : 割り当てるメモリ（メモリ量が多いほど使用料金も高くなる）
    - `--entry-point` : エントリーポイントの関数名
    - 参考 : https://cloud.google.com/sdk/gcloud/reference/functions/deploy?hl=ja#--region

尚、エントリーポイントとなる関数を含むコードは、`main.py` のファイル名にする必要があることに注意。


### 3. Cloud Functions の動作テスト

#### ☆ GUI 使用時
GUI を使用して、作成したCloud Functions の動作テストする場合は、以下の手順で実行できる。

1. Cloud Functions の [GUI 画面](https://console.cloud.google.com/functions/list?hl=ja&organizationId=0&project=my-project2-303004) に移動する
1. 作成した Cloud Functions を選択する
1. 「テスト」タグを選択する
1. トリガーとなるイベントに、json 形式のリクエストデータを入力する
1. 「関数をテストする」ボタンをクリック
1. 出力画面に、作成した Cloud Functions からのレスポンス結果が表示される。

<image src="https://user-images.githubusercontent.com/25688193/96669621-88711080-1398-11eb-8094-e86589c698e8.png" width="400">

#### ☆ GUI 非使用時（コマンド使用）

- `curl` コマンドで Cloud Function にリクエスト処理（＝jsonデータの送信）
    ```sh
    curl -X POST https://${REGION}-${PROJECT_ID}.cloudfunctions.net/${FUNCTION_NAME} -H "Content-Type: application/json" -d '{"message" : "Hello Cloud functions"}'
    ```