# PostgreSQL CLI を使用して PostgreSQL データベースの CRUD 処理を行う（docker 使用）

## ■ 方法

1. PostgreSQL サーバーの `docker-compose.yml` を作成する<br>
    ```yml
    version: '3'
    services:
      postgresql-server:
        image: postgres:14
        container_name: postgresql-container
        ports:
          - 5432:5432
        volumes:
          - ${PWD}/postgresql/db:/var/lib/postgresql/data/
          - ${PWD}/postgresql/postgresql.conf:/etc/postgresql/postgresql.conf
        environment:
          - POSTGRES_PASSWORD=1234    # sudo ユーザのパスワード
          - POSTGRES_USER=postgres    # sudo ユーザのユーザ名（デフォルト : postgres）
        command: -c 'config_file=/etc/postgresql/postgresql.conf'
    ```

    ポイントは、以下の通り

    - PostgreSQL がインストールされている docker image として、`postgres:14` の docker image を使用している

    - PostgreSQL データベースの実体は、docker image 内の `/var/lib/postgresql/data` ディレクトリ以下にあるので、`volumes` タグでこのディレクトリの内容をローカル環境と同期するようにしている。
    
    - `postgresql.conf` は、PostgreSQL サーバーの各種設定ファイルであるが、デフォルトでは、docker image 内の`/var/lib/postgresql/data` ディレクトリ以下にある `postgresql.conf` が読み込まれる動作になる。
    
        そのため、ローカル環境から作成した `postgresql.conf` で PostgreSQL サーバーを動作させるために、以下の処理を行っている
    
        1. `volumes` タグを使用して、ローカル環境の `${PWD}/postgresql/postgresql.conf` を docker image 内の `/etc/postgresql/postgresql.conf` に同期させる
    
        1. `command: -c 'config_file=/etc/postgresql/postgresql.conf'` で、`/etc/postgresql/postgresql.conf` にある `postgresql.conf` で PostgreSQL サーバーが起動するようにする

    - 環境変数 `POSTGRES_PASSWORD` に sudo ユーザのパスワードを設定する

    - 環境変数 `POSTGRES_USER` に sudo ユーザーのユーザー名を設定する。この環境変数を明示しない場合は、デフォルト値として `postgres` の sudo ユーザーが使用される

1. `postgresql.conf` を作成する<br>
    `postgresql/postgresql.conf` に PostgreSQL サーバーの各種設定ファイルを定義する
    ```conf
    # 例
    listen_addresses = '*'  # PostgreSQL サーバの IP アドレス
    port = 5432             # PostgreSQL サーバのポート番号
    max_connections = 200   # 同時接続数
    ```

    > このローカル環境から作成した `postgresql.conf` は、以下の処理により、PostgreSQL サーバーに反映される動作になっている
    > 1. `volumes` タグを使用して、ローカル環境の `${PWD}/postgresql/postgresql.conf` を docker image 内の `/etc/postgresql/postgresql.conf` に同期させる
    > 1. `command: -c 'config_file=/etc/postgresql/postgresql.conf'` で、`/etc/postgresql/postgresql.conf` にある `postgresql.conf` で PostgreSQL サーバーが起動するようにする

1. PostgreSQL サーバーを起動する<br>
    ```sh
    docker-compose -f docker-compose.yml stop
    docker-compose -f docker-compose.yml up -d
    ```

1. PostgreSQL サーバーに接続する<br>
    PostgreSQL サーバーの docker コンテナに接続した上で、`psql`　コマンドで（docker コンテナ内の）PostgreSQL サーバーに接続する
    ```sh
    docker exec -it postgresql-container /bin/bash -c "psql -h localhost -U postgres"
    ```

    > コンテナ内通信で PostgreSQL サーバーに接続するので、ホスト名は `localhost` にしている

1. PostgreSQL データベースの CRUD 処理を行う<br>

    1. データベースを作成する<br>
        PostgreSQL サーバーに接続後、以下のコマンドを実行する
        ```sh
        CREATE DATABASE ${DATABESE_NAME};
        ```
        ```sh
        # 例
        CREATE DATABASE test_db;
        ```

    1. データベースの一覧確認する<br>
        PostgreSQL サーバー内で以下のコマンドを実行する
        ```sh
        \l
        ```

    1. 作成したデータベースに接続する<br>
        PostgreSQL サーバーに接続後、以下のコマンドを実行する
        ```sh
        \c ${DATABESE_NAME}
        ```
        ```sh
        # 例
        \c test_db
        ```

    1. 作成したデータベース内にテーブルを追加する<br>
        PostgreSQL サーバー内で、以下のコマンドを実行する
        ```sql
        CREATE TABLE ${TABLE_NAME} (
            ${COL_NAME1} VARCHAR(8),
            ${COL_NAME2} VARCHAR(8)
        );
        ```
        ```sql
        # 例
        CREATE TABLE account(
            id VARCHAR(8),
            name VARCHAR(8)
        );
        ```

    1. データベースを確認する<br>
        PostgreSQL サーバー内で以下のコマンドを実行する
        ```sh
        \d
        ```

    1. PostgreSQL サーバーから exit する<br>
        PostgreSQL サーバー内で以下のコマンドを実行する
        ```sh
        \q
        ```

## ■ 参考サイト

- https://zenn.dev/re24_1986/articles/b76c3fd8f76aec