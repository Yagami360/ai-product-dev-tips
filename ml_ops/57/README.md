# 【GCP】Google Cloud SQL を使用して SQL インスタンス上の MySQL データベースの CRUD 処理を行う

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


1. Cloud SQL Auth Proxy を起動し、SQL インスタンスへの接続可能状態にする<br>
    SQL インスタンスへの接続方法には、いくつかの種類があるが、ここでは最も汎用的な Cloud SQL Auth Proxy を使用して SQL インスタンスに接続する方法を記載する

    1. Cloud SQL Auth Proxy をダウンロードしてインストールする<br>
        - MacOS（64bit）の場合
            ```sh
            curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64
            chmod +x cloud_sql_proxy
            ```

        - MacOS（M1）の場合
            ```sh
            curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.arm64
            chmod +x cloud_sql_proxy
            ```

        - Linux（64bit）の場合
            ```sh
            wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
            chmod +x cloud_sql_proxy
            ```

    1. Cloud SQL Auth Proxy を起動する<br>
        Cloud SQL Auth Proxy を起動して、SQL インスタンスへ接続可能な状態にする
        ```sh
        ./cloud_sql_proxy -instances=${INSTANCE_CONNECTION_NAME}=tcp:3306
        ```
        - `${INSTANCE_CONNECTION_NAME}` : Cloud SQL インスタンスの接続名。`${PROJECT_ID}:${REGION}:${INSTANCE_ID}` の形式になる

        Cloud SQL Auth Proxy を起動すると、以下のようなメッセージが出力され、実行待ち状態になる
        ```sh
        2022/05/29 15:00:53 current FDs rlimit set to 1048575, wanted limit is 8500. Nothing to do here.
        2022/05/29 15:00:58 Listening on 127.0.0.1:3306 for my-project2-303004:us-central1:mysql-instance-220528
        2022/05/29 15:00:58 Ready for new connections
        2022/05/29 15:00:58 Generated RSA key in 92.981495ms
        ```

        > 実際の接続は、後述の `mysql` コマンドで行う

        > シェルスクリプトで上記コマンドを実行した場合は、実行待ち状態になって、別タブで `mysql` コマンドを実行する必要があるので、Cloud SQL Auth Proxy の docker コンテナを作成し、その docker コンテナ内で上記コマンドを行う方法がベター
        > - https://cloud.google.com/sql/docs/sqlserver/connect-docker?hl=ja

1. SQL インスタンスに接続する<br>
    - `gcloud sql connect` コマンドで接続する場合<br>
        ```sh
        gcloud sql connect ${SQL_INSTANCE_NAME} --user=root
        ```

    - MySQL クライアントで接続する場合<br>
        1. MySQL をインストールする<br>
            - MacOS の場合
                ```sh
                brew install mysql
                ```
            - Linux の場合
                ```sh
                sudo apt install mysql-server
                ```

        1. MySQL クライアントコマンドで SQL サーバー上の MySQL データベースに接続する
            ```sh
            mysql -u root -p --host 127.0.0.1 --port 3306
            ```
            > 上記コマンド入力後、パスワードの入力が求められるので、SQL インスタンスのパスワードを入力して接続する

            > SQL インスタンスに root ユーザーを作成済みなので、`mysql_secure_installation` コマンドで MySQL サーバーの root ユーザーを作成する処理は不要

1. Cloud SQL インスタンス上でデータベースの CRUD 処理を行う<br>
    `gcloud sql connect` or `mysql` コマンドで SQL インスタンス接続後、SQL 構文でデータベースの CRUD 処理ができるようになる

    1. MySQL データベースを作成する
        ```sql
        CREATE DATABASE sample_database;
        ```
    1. データベースにデータを追加する
        ```sql
        USE sample_database;
        CREATE TABLE entries (name VARCHAR(255), gender VARCHAR(255), entryID INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(entryID));
            INSERT INTO entries (name, gender) values ("Yagami", "male");
            INSERT INTO entries (name, gender) values ("Yagoo", "male");
        ```
    1. 作成したデータベースを取得する
        ```sql
        SELECT * FROM entries;
        ```
        ```sql
        mysql> SELECT * FROM entries;
        +--------+--------+---------+
        | name   | gender | entryID |
        +--------+--------+---------+
        | Yagami | male   |       1 |
        | Yagoo  | male   |       2 |
        +--------+--------+---------+
        2 rows in set (1.71 sec)
        ```

## ◎ 参考サイト

- https://cloud.google.com/sql/docs/mysql?hl=ja
- https://cloud.google.com/sql/docs/mysql/connect-instance-auth-proxy?hl=ja#macos-64-bit
