# 【MySQL】MySQL に保存したジョブデータをバッチ単位で処理する Web-API（FastAPI + uvicorn + gunicorn + MySQL + SQLAlchemy + docker + docker-compose での構成）

ここでは、以下のような処理を行う Web-API を構築する

> API 構築図を追加

1. API サーバーにて、推論リクエスト受付時にジョブデータ｛ジョブID・推論用データ｝を MySQL に保管する。このとき、API サーバーでは推論処理は行わない
1. バッチ管理サーバーにて、MySQL に保存されているジョブデータ｛ジョブID・推論用データ｝を定期的にポーリングし、バッチ単位（＝ここでは例として、推論未実行の全ての画像）で API での推論処理を行う
1. バッチ単位での推論結果は、バッチ管理サーバーにて MySQL に保管される


## ■ 方法


> 現状の構成では、`models.py` の `JobTable` のクラス変数を変更しても、MySQL データベースのテーブルデータを削除しない限りは、変更したクラス変数は反映されないことに注意

> ジョブIDは重複のない値になるので、`job_id = Column( String(255), primary_key=True)` の `primary_key=True` 引数でプライマリーキーとして設定している。これにより、job_id の値に一致するテーブルを選択するメソッド `select_job_id()` が実現可能になる。

## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter4_serving_patterns/batch_pattern