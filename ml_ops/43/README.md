# 推論時間が異なる複数の API から構成される Web-API において、推論結果を複数段階に分けてレスポンスする（FastAPI + uvicorn + gunicorn + docker + docker-compose での構成）

推論時間が異なる複数の API から構成される Web-API において、全ての API を同期的に処理すると、それらの API を並列処理で実行した場合でも、最も推論時間の長い API の処理時間になってしまう問題がある。

ここでは、このような推論時間が異なる複数の API から構成される Web-API において、推論時間が短い API は同期処理での API にしてリクエストに対して同期的にレスポンスさせ、推論時間が長い API は非同期処理での API にして非同期でレスポンスさせるといった具合で、推論結果を複数段階に分けてレスポンスする方法を記載する。

このように推論結果を複数段階に分けてレスポンスすることで、推論時間が異なる複数の API から構成される Web-API を推論時間を損なうことなく実行できるようになるメリットがある

<img src="https://user-images.githubusercontent.com/25688193/126888260-6d28dfef-7532-4b0f-9ca4-a96a14d3e470.png" width="500"><br>

## ■ 方法


## ■ 参考サイト

- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter4_serving_patterns/sync_async_pattern