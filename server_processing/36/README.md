# FastAPI を使用した非同期処理の Web-API の構築（FastAPI + uvicorn + gunicorn + redis + バッチサーバー + docker での構成）

「[FastAPI での非同期処理（FastAPI + uvicorn + gunicorn + docker での構成）](https://github.com/Yagami360/MachineLearning_Tips/tree/master/server_processing/35)」記載の方法をベースに、更に以下のコンポーネントを追加する

- プロキシサーバー（uvicorn + gunicorn + FastAPI）で非同期処理を行うジョブを定義
- redis をジョブキューとして使用
- バッチサーバー（＝ジョブの投入から終了までを管理するサーバー）で、redis のジョブキューを定期的にポーリングして、キューにデータが存在すれば API サーバーにリクエストする


> API 構成図を追加

