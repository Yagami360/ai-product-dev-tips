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
      "${DSNの値}"
      "https://c3773729429b4e1a8b2c7d35424178f4@o1171856.ingest.sentry.io/6266790",

      # Set traces_sample_rate to 1.0 to capture 100%
      # of transactions for performance monitoring.
      # We recommend adjusting this value in production.
      traces_sample_rate=1.0
  )
  ```

1. FastAPI を使用した Web-API のコードを作成する

1. FastAPI を使用した Web-API の Dockerfile を作成する
  ```dockerfile
  ```
  ポイントは、以下の通り

  - `RUN pip3 install --upgrade sentry-sdk` で　Sentry の Python SDK をインストールしている


## ■ 参考サイト

- https://zenn.dev/a_ichi1/articles/f85f1b53b474cb
- https://qiita.com/Chanmoro/items/a9cbde57fd6c0926b5b4