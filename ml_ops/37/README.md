# 【MySQL】MySQL に保存したジョブデータをバッチ単位で処理する Web-API（FastAPI + uvicorn + gunicorn + MySQL + SQLAlchemy + docker + docker-compose での構成）

ここでは、以下のような処理を行う Web-API を構築する

> API 構築図を追加

1. API サーバーにて、推論リクエスト受付時にジョブデータ｛ジョブID・推論用データ｝を MySQL に保管する。このとき、API サーバーでは推論処理は行わない
1. バッチ管理サーバーにて、MySQL に保存されているジョブデータ｛ジョブID・推論用データ｝を定期的にポーリングし、バッチ単位（＝ここでは例として、推論未実行の全ての画像）で API での推論処理を行う
1. バッチ単位での推論結果は、バッチ管理サーバーにて MySQL に保管される


## ■ 方法

## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter4_serving_patterns/batch_pattern