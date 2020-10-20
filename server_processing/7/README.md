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

## 実現方法
Cloud Functions を利用するには、以下の処理が必要
1. Cloud Functions の作成
1. Cloud Functions 用のコードの作成
1. 作成したコードのデプロイ処理

これらの処理をブラウザの GUI で行うのは面倒で使いにくい。（特にブラウザエディタでのコードの修正とデプロイ処理）
VSCode などのエディタでコード修正後、`gcloud` のコマンドを使用して Cloud Functions 作成＆デプロイ処理を行う流れにしたほうが使いやすい。

Cloud Functions の作成からデプロイ処理までを行うコマンドには、以下のコマンドがある。
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
