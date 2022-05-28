# 【GCP】Google Cloud SQL を使用して SQL インスタンス上に MySQL データベースを作成する

## ◎ 方法

1. Google Cloud SQL API の有効化<br>
    作成した SQL インスタンスの MySQL にアクセスし、データベースの CRUD 処理を行うためには、Google Cloud SQL API の Python クライアントライブラリを用いて行う必要があるので、まず Google Cloud SQL API を有効化する

    - GUI で行う場合<br>
        「[GCP のコンソール画面](https://console.cloud.google.com/marketplace/product/google/sql-component.googleapis.com?q=search&referrer=search&hl=ja&project=my-project2-303004)」から、Google Cloud SQL API を有効化する

    - CLI で行う場合<br>
        ```sh
        gcloud services enable sqladmin.googleapis.com
        ```

1. SQL インスタンスを作成する<br>
    まず MySQL 用の SQL インスタンス（VMインスタンス）を作成する。

    - GUI で行う場合<br>
        1. 「[GCP の SQL コンソール画面](https://console.cloud.google.com/sql?hl=ja&project=my-project2-303004)」から、「インスタンスを作成」ボタンをクリックする<br>
            <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170828315-2afee7d4-d950-411d-8fff-ae9cb0e2ae52.png"><br>
        1. 今回は、MySQL 用の SQL インスタンス（VMインスタンス）を作成するので「MySQL を選択」ボタンをクリックする<br>
            <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170828337-c0949cae-4832-41f1-84b9-8bf0a67950b0.png"><br>
        1. 「インスタンスID」と「パスワード」を入力して、「インスタンスを作成」ボタンをクリックすることで、SQL インスタンスが作成される。<br>
            <img width="500" alt="image" src="https://user-images.githubusercontent.com/25688193/170828585-1e278f36-5337-4a2d-b6bc-31ff0627165e.png"><br>

    - CLI で行う場合<br>
        1. SQL インスタンスを作成する
            ```sh
            gcloud sql instances create ${SQL_INSTANCE_NAME} \
                --database-version=MYSQL_8_0 \
                --cpu=${N_CPUS} \
                --memory=${MEMORY_SIZE} \
                --region=${REGION}
            ```

        1. 作成した SQL インスタンスの root ユーザーのパスワードを設定する
            ```sh
            gcloud sql users set-password root \
                --host=% \
                --instance ${SQL_INSTANCE_NAME} \
                --password ${PASSWORD}
            ```

        > 作成した SQL インスタンスは `gcloud sql instances list` コマンドで確認できる

    > SQL インスタンスの削除後、約 7 日はそのインスタンス名を再利用できないことに注意

1. SQL インスタンスへ接続する<br>
    SQL インスタンスへの接続方法には、いくつかの種類がある

    - 【方法１】シェルスクリプト上から SQL インスタンスに接続する場合<br>
        1. `gcloud sql connect` コマンドで SQL インスタンスに接続する<br>
            ```sh
            gcloud sql connect ${SQL_INSTANCE_NAME} --user=root
            ```
        1. root ユーザーのパスワードを入力すれば、SQL インスタンスに接続できる<br>

    - 【方法２】xxx<br>
        1. xxx

    - 【方法３】Cloud SQL Auth Proxy を使用して SQL インスタンスへの接続する場合<br>
        1. Cloud SQL Auth Proxy をダウンロードしてインストールする<br>
            ```sh
            ```

        1. Cloud SQL に接続するためのサービスアカウントを作成する<br>
            ```sh
            ```

        - 参考サイト
            - https://cloud.google.com/sql/docs/mysql/sql-proxy?hl=ja


1. Cloud SQL インスタンス上でデータベースの CRUD 処理を行う<br>
    SQL インスタンス接続後、SQL 構文でデータベースの CRUD 処理ができるようになる

    1. MySQL データベースを作成する
        ```sql
        CREATE DATABASE sample-database;
        ```
    1. データベースにデータを追加する
        ```sql
        USE sample-database;
        CREATE TABLE entries (name VARCHAR(255), gender VARCHAR(255),
            entryID INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(entryID));
            INSERT INTO entries (name, age) values ("Yagami", "male");
            INSERT INTO entries (name, age) values ("Yagoo", "male");
        ```
    1. 作成したデータベースを取得する
        ```sql
        SELECT * FROM entries;
        ```

## ◎ 参考サイト

- https://cloud.google.com/sql/docs/mysql?hl=ja
