# FastAPI を使用した非同期処理での Web-API の構築（FastAPI + uvicorn + gunicorn + redis + バッチサーバー + docker での構成）

「[FastAPI での非同期処理（FastAPI + uvicorn + gunicorn + docker での構成）](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/35)」記載の方法をベースに、更に以下のコンポーネントを追加する

- プロキシサーバー（uvicorn + gunicorn + FastAPI）で非同期処理を行うジョブを定義
- redis をジョブキューとして使用
- バッチサーバー（＝ジョブの投入から終了までを管理するサーバー）で、redis のジョブキューを定期的にポーリングして、キューにデータが存在すれば API サーバーにリクエストする


> API 構成図を追加

<img src="https://user-images.githubusercontent.com/25688193/121313477-646f3900-c941-11eb-9c01-30fee4ca72f8.png" width="300"><br>

## ■ 使用法

1. プロキシサーバーの構築
1. redis の構築
1. バッチサーバーの構築
1. API サーバーの構築
1. docker-compose で API 構成
1. リクエスト処理

    > `requests` モジュールを用いて POST メリットでリクエストボディ（jsonデータ）を送信する際に、Flask では `json.dumps()` を用いて dict 型データを JSON 形式に変換する必要する必要があったが、FastAPI では、`json.dumps()` を行う必要がないことに注意

## ■ 参考サイト
- https://qiita.com/icoxfog417/items/07cbf5110ca82629aca0