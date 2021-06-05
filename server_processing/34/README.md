# FastAPI での非同期処理

FastAPI での非同期処理を行う場合は、まずpython3 の `asyncio` モジュールの機能である `async def` を使用して関数を定義する<br>
但し、`async def` 単体では、非同期処理（マルチスレッド処理）にはならないことに注意。

そして、FastAPI の `BackgroundTask` を使用して

- FastAPI で非同期処理を行うコード例
    ```python
    ```

## ■ 参考サイト
- https://qiita.com/juri-t/items/91e561509aa7ca6e7d38