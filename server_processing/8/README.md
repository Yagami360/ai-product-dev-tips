# 【GCP】Cloud Run を利用したサーバーレス Web-API

- Cloud Run と Cloud Functions の違い
    - Cloud Runは「**docker コンテナ**をサーバーレスで実行する」サービス
    - Cloud Functions は「**コード**をサーバレスで実行する」サービス

- Cloud Run 導入のメリット
    - Cloud Functions と同様に、サーバーのオートスケーリング、ロードバランサーなどを自動的に行ってくれる。
    - Cloud Functions とは異なり、コンテナをサーバーレスで実行するので、Cloud Run 用のコードの書き換えが不要？

- Cloud Run 導入のデメリット
    - GPU インスタンスは使えない？
        - Cloud Run for Anthos では
    - デプロイ処理に時間がかかり、デバッグ作業が非効率になる
        - [コンテナ イメージをローカルでテストする](https://cloud.google.com/run/docs/testing/local?hl=ja) の方法で解決可能？
    - サーバ上のファイルに書き込むことができるが、メモリ上の一時的なもののため、停止すると失われる

## 実現方法
Cloud Run は、以下の手順で利用できる。

0. [Google Container Registry API](https://console.cloud.google.com/apis/library/containerregistry.googleapis.com?hl=ja&_ga=2.255813448.1982938393.1603197893-757162934.1603197893) を有効化
1. api コードの作成し、docker image を作成
1. 作成した docker image を GCP の Container Registry にアップロード
1. アップロードした docker image を元に Cloud Run を作成する（=docker image を Cloud Run にデプロイ）
1. Cloud Run の動作確認

### 1. api コードの作成し、docker image を作成
`dockerfile` から、作成した api コード `app.py` の docker image を作成する

- docker image の作成
    ```sh
    $ docker build -t gcr.io/${PROJECT_ID}/${IMAGE_NAME} .
    ```

### 2. 作成した docker image を GCP の Container Registry にアップロード
以下のコマンドを用いて、作成した docker image を GCP の Container Registry にアップロードする。

- docker image のアップロード
    ```sh
    $ docker push gcr.io/${PROJECT_ID}/${IMAGE_NAME}
    ```

- docker image の作成＆アップロード
    ```sh
    $ gcloud builds submit --tag gcr.io/${PROJECT_ID}/${IMAGE_NAME}
    ```

アップロードされた docker image は、[GCP の Container Registry の GUI](https://console.cloud.google.com/gcr/images/my-project2-303004?project=my-project2-303004) に存在する。（アップロードされた docker image の削除等もこの画面上から行える）


### 3. アップロードした docker image を元に Cloud Run を作成する（=docker image を Cloud Run にデプロイ）
Cloud Run の [GUI 画面](https://console.cloud.google.com/run?hl=ja&organizationId=0&project=my-project2-303004)、又は、以下のコマンドを用いて、アップロードした docker image を元に Cloud Run を作成する

- docker image を Cloud Run にデプロイ
    ```sh
    $ gcloud beta run deploy ${SERVICE_NAME} --image gcr.io/${PROJECT_ID}/${IMAGE_NAME} --region=${REGION}
    ```
    - https://cloud.google.com/sdk/gcloud/reference/beta/run/deploy#SERVICE

### 4. Cloud Run の動作確認

- `app.py` の `@app.route('/')` アクセス時の挙動は、Cloud Run の [GUI 画面](https://console.cloud.google.com/run?hl=ja&organizationId=0&project=my-project2-303004) の項目「URL」のリンク先から確認できる。
- `app.py` の リクエストメッセージ受信時の動作は、リクエスト処理のコードを実装するか、以下のコマンドで確認できる
    ```sh
    $ curl -H "Content-type: application/json"  -X POST -d "{\"name\":\"test\"}" ${HOST_ADRESS}:${PORT}/hello_world
    ```
    - 作成した Could Run の アドレス `${HOST_ADRESS}` は、[GUI 画面](https://console.cloud.google.com/run?hl=ja&organizationId=0&project=my-project2-303004) の項目「URL」のアドレスを設定すれば良い
    