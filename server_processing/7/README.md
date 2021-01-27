# 【GCP】Cloud Functions を利用したサーバーレス Web-API

- Cloud Functions 導入のメリット
    - サーバーのオートスケーリング、ロードバランサーなどを自動的に行ってくれる。

- Cloud Functions 導入のデメリット
    - リクエスト処理やレスポンス処理を行うコードを場合によっては、Cloud Functions 用に一部書き換える必要がある
        - 言い換えると、サーバー上で動作していた既存のコードが、Cloud Functions 上では動作しないケースがある
        - 特に IO 関係はコードを書き換える必要が出てくる可能性が高い（GCP Storege 利用が必要になって、既存の `os` モジュールが使えなくなるなど）
    - デプロイ処理に時間がかかり、デバッグ作業が非効率になる
        - [ローカルでの関数の実行](https://firebase.google.com/docs/functions/local-emulator?hl=ja) の方法で解決可能？

- 確認中
    - Cloud Functions でも GPU が必要な処理（PyTorch）などを実行できるのか？

## ■ 実現方法
Cloud Functions は、以下の手順で利用できる
1. Cloud Functions 用のコードの作成
1. Cloud Functions の作成（＝作成したコードのデプロイ処理）
1. Cloud Functions の動作テスト

### 1&2. Cloud Functions 用のコードの作成＆Cloud Functions の作成（＝作成したコードのデプロイ処理）

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
