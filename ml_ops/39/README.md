# 推論結果を Redis にキャッシュし、同じ入力データでの Web-API の推論処理を高速化する（FastAPI + uvicorn + gunicorn + redis + docker + docker-compose での構成）


## ■ 方法

1. xxx


1. レスポンス処理する

    １回目のリクエストに対してのログデータ
    ```sh
    2021-07-11 18:43:01 INFO predict START job_id=f3d237
    registering cache: in_images/000001_0.jpg
    2021-07-11 18:43:02 INFO predict END job_id=f3d237, elapsed_time [ms]=445.93096
    [CacheDataRedisJob] time 18:43:02 | FileName in_images/000001_0.jpg を登録しました
    2021-07-11 18:43:02 INFO predict START job_id=77e8de
    registering cache: in_images/000010_0.jpg
    2021-07-11 18:43:02 INFO predict END job_id=77e8de, elapsed_time [ms]=258.72540
    [CacheDataRedisJob] time 18:43:02 | FileName in_images/000010_0.jpg を登録しました
    2021-07-11 18:43:02 INFO predict START job_id=a39dde
    registering cache: in_images/000020_0.jpg
    2021-07-11 18:43:03 INFO predict END job_id=a39dde, elapsed_time [ms]=910.98833
    [CacheDataRedisJob] time 18:43:03 | FileName in_images/000020_0.jpg を登録しました
    2021-07-11 18:43:03 INFO predict START job_id=85f054
    registering cache: in_images/000028_0.jpg
    2021-07-11 18:43:04 INFO predict END job_id=85f054, elapsed_time [ms]=234.86805
    [CacheDataRedisJob] time 18:43:04 | FileName in_images/000028_0.jpg を登録しました
    2021-07-11 18:43:04 INFO predict START job_id=35f7e0
    registering cache: in_images/000038_0.jpg
    2021-07-11 18:43:04 INFO predict END job_id=35f7e0, elapsed_time [ms]=243.07585
    [CacheDataRedisJob] time 18:43:04 | FileName in_images/000038_0.jpg を登録しました
    ```

    ２回目以降のリクエストに対してのログデータ
    ```sh
    2021-07-11 18:45:32 INFO predict START job_id=25e4a7
    cache hit: in_images/000001_0.jpg
    2021-07-11 18:45:32 INFO predict END job_id=25e4a7, elapsed_time [ms]=4.23503
    2021-07-11 18:45:32 INFO predict START job_id=bb2678
    cache hit: in_images/000010_0.jpg
    2021-07-11 18:45:32 INFO predict END job_id=bb2678, elapsed_time [ms]=3.52383
    2021-07-11 18:45:32 INFO predict START job_id=f06154
    cache hit: in_images/000020_0.jpg
    2021-07-11 18:45:32 INFO predict END job_id=f06154, elapsed_time [ms]=2.47335
    2021-07-11 18:45:32 INFO predict START job_id=66919a
    cache hit: in_images/000028_0.jpg
    2021-07-11 18:45:32 INFO predict END job_id=66919a, elapsed_time [ms]=1.70183
    2021-07-11 18:45:32 INFO predict START job_id=e4599e
    cache hit: in_images/000038_0.jpg
    2021-07-11 18:45:32 INFO predict END job_id=e4599e, elapsed_time [ms]=3.32642
    ```

    初回のレスポンスでは、キャッシュデータが存在しないので、推論 API で推論を行い処理に時間がかかっているが、２回目以降のレスポンスに関しては、キャッシュデータを使用するので処理が早くなっていることがわかる

## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter4_serving_patterns/prediction_cache_pattern