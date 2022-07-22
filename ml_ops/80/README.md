# PostgreSQL CLI を使用して PostgreSQL データベースの CRUD 処理を行う

## ■ 方法

1. PostgreSQL CLI (postgresql-client) をインストールする
    - MacOS の場合
        ```sh
        brew update
        brew install postgresql
        ```

    - Ubutnu の場合
        ```sh
        sudo apt install -y postgresql-client
        ```

1. 【オプション】`postgresql.conf` を修正する<br>
    `postgresql.conf` は、PostgreSQL に関する基本的な設定を記述するファイルで、PostgreSQL をインストールしたディレクりの中の data ディレクトリの中に格納されている。

    今回のケース（MacOS）では、`/usr/local/var/postgres/postgresql.conf` に存在する。

    `postgresql.conf` を修正することで、PostgreSQL サーバーのポートなどを変更することができる（今回はデフォルトのままにする）

    変更した `postgresql.conf` は、以下のコマンドで反映できる
    ```sh
    systemctl reload postgresql.service
    ```

1. PostgreSQL サーバーを起動する<br>
    - MacOS の場合<br>
        ```sh
        brew services start postgresql
        ```

    - Ubuntu の場合<br>
        ```sh
        ```

    > 初期ロールとして、OSユーザと同名の postgres が存在します。postgres ロールにはパスワードが設定されていないので、アクセス制御の設定を施す前に、先にパスワードの設定を行います。

1. PostgreSQL サーバーに接続する<br>
    ```sh
    psql postgres
    ```

    > PostgreSQL インストール後に、初期のロール名 `postgres` が存在するが、この `postgres` ロールで PostgreSQL サーバーに接続している

<!--
1. 初期ロール `postgres` に sudo 権限を付与する<br>
    PostgreSQL サーバー内で、以下のコマンドを実行する
    ```sh
    createuser postgres SUPERUSER
    ```
    > 初期のロール名 `postgres` には、sudo 権限が付与されていないので、上記コマンドで sudo 権限を付与している
-->

1. データベースを作成する<br>
    PostgreSQL サーバー外で、以下のコマンドを実行する
    ```sh
    createdb ${DATABESE_NAME} owner=postgres
    ```
    ```sh
    # 例
    createdb test_db owner=postgres
    ```

    > PostgreSQL サーバー内ではなく、サーバー外から実行するコマンドであることに注意

1. データベースの一覧確認する<br>
    PostgreSQL サーバー内で以下のコマンドを実行する
    ```sh
    \l
    ```
    ```sh
                            List of databases
    Name    | Owner | Encoding | Collate | Ctype | Access privileges 
    -----------+-------+----------+---------+-------+-------------------
    postgres  | sakai | UTF8     | C       | C     | 
    template0 | sakai | UTF8     | C       | C     | =c/sakai         +
            |       |          |         |       | sakai=CTc/sakai
    template1 | sakai | UTF8     | C       | C     | =c/sakai         +
            |       |          |         |       | sakai=CTc/sakai
    test_db   | sakai | UTF8     | C       | C     | 
    ```

1. 作成したデータベースに接続する<br>
    PostgreSQL サーバー外で、以下のコマンドを実行する
    ```sh
    psql ${DATABESE_NAME} -U ${USER_NAME}
    ```
    ```sh
    # 例
    psql test_db -U postgres
    ```

    > PostgreSQL サーバー内ではなく、サーバー外から実行するコマンドであることに注意

1. 作成したデータベース内にテーブルを追加する<br>
    PostgreSQL サーバー内で、以下のコマンドを実行する
    ```sh
    # 例
    CREATE TABLE account(id varchar(8), name varchar(8));
    ```

1. データベースを確認する<br>
    PostgreSQL サーバー内で以下のコマンドを実行する
    ```sh
    \d
    ```
    ```sh
            List of relations
    Schema |  Name   | Type  |  Owner   
    --------+---------+-------+----------
    public | account | table | postgres
    (1 row)
    ```

1. PostgreSQL サーバーから終了する<br>
    PostgreSQL サーバー内で以下のコマンドを実行する
    ```sh
    \q
    ```

1. PostgreSQL サーバーを停止する<br>
    - MacOS の場合<br>
        ```sh
        brew services stop postgresql
        ```

    - Ubuntu の場合<br>
        ```sh
        ```

## ■ 参考サイト

- https://qiita.com/ipepi/items/58dedbc0434fa9ea3b71
- https://densan-hoshigumi.com/server/postgresql-remote-connection