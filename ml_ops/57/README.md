# 【GCP】Google Cloud SQL を使用して MySQL に Web-API のログデータを書き込む（FastAPI + uvicorn + gunicorn + MySQL + docker + docker-compose での構成）

## ◎ 方法

1. Google Cloud SQL API の有効化<br>
    作成した SQL インスタンスの MySQL にアクセスし、データベースの CRUD 処理を行うためには、Google Cloud SQL API の Python クライアントライブラリを用いて行う必要があるので、まず Google Cloud SQL API を有効化する

    - GUI で行う場合<br>
        「[GCP のコンソール画面](https://console.cloud.google.com/marketplace/product/google/sql-component.googleapis.com?q=search&referrer=search&hl=ja&project=my-project2-303004)」から、Google Cloud SQL API を有効化する

    - CLI で行う場合<br>
        ```sh
        ```

1. SQL インスタンスを作成する<br>
    まず MySQL 用の SQL インスタンス（VMインスタンス）を作成する。

    - GUI で行う場合<br>
        「[GCP の SQL コンソール画面](https://console.cloud.google.com/sql?hl=ja&project=my-project2-303004)」から、


    - CLI で行う場合<br>
        ```sh
        gcloud sql instances create ${INSTANCE_NAME} \
            --cpu=${NUMBER_CPUS} \
            --memory=${MEMORY_SIZE} \
            --region=${REGION}
        ```

        ```sh
        # コマンド例
        gcloud sql instances create myinstance \
            --database-version=MYSQL_8_0 \
            --cpu=2 \
            --memory=7680MB \
            --region=us-central1
        ```

1. Cloud SQL Auth Proxy を使用して SQL インスタンスへの接続する<br>
    SQL インスタンスへの接続方法には、いくつかの種類があるが、ここでは、Cloud SQL Auth Proxy での接続する

    1. Cloud SQL Auth Proxy をダウンロードしてインストールする<br>
        ```sh
        ```

    1. Cloud SQL に接続するためのサービスアカウントを作成する<br>


    - 参考サイト
        - https://cloud.google.com/sql/docs/mysql/sql-proxy?hl=ja


1. Web-API のコードを作成する<br>

1. Web-API の Dockerfile を作成する<br>

1. `docker-compose.yml` を作成する<br>

1. Web-API に対してリクエスト処理を行う<br>


## ◎ 参考サイト

- https://cloud.google.com/sql/docs/mysql?hl=ja
