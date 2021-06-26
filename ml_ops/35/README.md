# 【MySQL】SQLAlchemy を使用して Python スクリプトから MySQL に接続する（docker + docker-compose での構成）

## 方法

1. SQLAlchemy の Python コードを作成する<br>
    SQLAlchemy を使用して、MySQL サーバーのデータベースに、CRUD 処理 [Create + Read + Update + Destory] するための Python スクリプトを作成する

1. MySQL サーバーの設定ファイル `my.cnf` を作成する<br>
    ```ini
    [client]
    default-character-set=utf8mb4

    [mysqld]
    character-set-server=utf8mb4
    collation-server=utf8mb4_unicode_ci
    ```

    > MySQL でのホスト名やポート番号も、この設定ファイル `my.cnf` から行える

    > この設定ファイル `my.cnf` は、後述の docker-compose の `volumes` タグで、MySQL docker image の `/etc/my.cnf` にマウントすることで、MySQL サーバーに反映させる.

1. MySQL サーバーの `docker-compose.yml` を作成する<br>
    ```yml
    ```

    ポイントは、以下の通り<br>
    - `environment` タグに MySQL の環境変数を追加<br>
        `environment` タグに、MySQL の docker image `mysql` で使用される環境変数 `MYSQL_ROOT_PASSWORD`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` を設定することで、その設定値を反映した MySQL サーバーが実行される

        > 各環境変数の意味は、「[【補足】MySQL の docker image `mysql` について](#MySQLのdockerimageについて)」を参照

        > MySQL サーバーのホスト名とポート番号を設定する環境変数は、用意されていないことに注意。ホスト名とポート番号は、MySQL 設定ファイル `etc/my.cnf` で設定できるが、特に設定しなかった場合は、デフォルト値の "localhost" と `3306` になる

    - コンテナ起動時の `command` は使用しない<br>
        MySQL の docker image `mysql` では、docker image 起動時に、エンドポイントのスクリプト `/entrypoint.sh` が実行され、`mysqld` コマンドが自動的に実行されので、コンテナ起動時に `command` タグで MySQL サーバーを起動する処理を行う必要はない

<!--
    - `restart: always`
        
    - `stdin_open: true` : コンテナの標準入力をオープンしたままにする。`docker run` での `-i` オプションに対応
-->

1. `docker-compose` コマンドで、MySQL サーバーを起動する<br>
    ```sh
    $ docker-compose -f docker-compose.yml stop
    $ docker-compose -f docker-compose.yml up -d
    ```

1. [オプション] MySQL サーバーの動作確認<br>
    1. MySQL サーバーのコンテナへの接続<br>
        ```sh
        $ docker exec -it mysql-container bash
        ```

    1. MySQL サーバーへログイン<br>
        新規ユーザー `user` でログインする場合は、MySQL サーバーのコンテナへ接続した状態で、以下のコマンドを実行する
        ```sh
        root@895bd83c83e0:/# mysql -u user -p
        Enter password: password
        ```

        接続完了後は、以下のような出力になる<br>
        ```sh
        Welcome to the MySQL monitor.  Commands end with ; or \g.
        Your MySQL connection id is 3
        Server version: 5.7.34 MySQL Community Server (GPL)

        Copyright (c) 2000, 2021, Oracle and/or its affiliates.

        Oracle is a registered trademark of Oracle Corporation and/or its
        affiliates. Other names may be trademarks of their respective
        owners.

        Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

        mysql> 
        ```

    1. データベース一覧の確認<br>
        MySQL サーバーに接続した状態で、以下のコマンドを実行することで、作成済みのデータベース一覧が確認できる。
        ```sh
        mysql> show databases;
        ```

        今回の設定では、以下の出力になっていれば、MySQL サーバーが正しく動作している
        ```sh
        +--------------------+
        | Database           |
        +--------------------+
        | information_schema |
        | test_db            |
        +--------------------+
        2 rows in set (0.03 sec)
        ```

    1. MySQL サーバーからログアウトする<br>
        ```sh
        mysql> exit
        ```

1. SQLAlchemy を使用した Python スクリプトを実行する
    ```sh
    $ python crud.py --debug
    ```

<a id="MySQLのdockerimageについて"></a>

## 【補足】MySQL の docker image `mysql` について
MySQL の docker image `mysql` を使用して MySQL サーバーを起動する場合は、docker 非使用時の「[【MySQL】SQLAlchemy を使用して Python スクリプトから MySQL に接続する](https://github.com/Yagami360/MachineLearning_Tips/tree/master/ml_ops/34)」のときのように、`mysql_secure_installation` コマンドで初期設定（=root ユーザーの作成）を行ったり、`mysql.server start` コマンドで MySQL サーバーを起動する処理は不要となる

- MySQL の docker image `mysql` のディレクトリ構造<br>
    - `/etc/mysql/my.cnf` : MySQL のグローバルオプション
    - `/docker-entrypoint-initdb.d` : ?
    - `/entrypoint.sh` : docker image 起動時のエントリーポイントスクリプト。`mysqld` コマンドが自動的に実行される

- MySQL の docker image `mysql` 起動時の動作<br>
    docker image 起動時（`docker run`）に、`/entrypoint.sh` が実行され、`mysqld` コマンドが自動的に実行される。<br>
    また、Ubuntu のユーザー名は `mysql` になる
    > このユーザー名 `mysql` は、MySQL のユーザー名ではないことに注意。MySQL のユーザー名は、環境変数 `` で設定できる

    ```sh
    $ docker logs ${MYSQL_CONTAINER_NAME}
    2021-06-26 02:57:31+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 5.7.34-1debian10 started.
    2021-06-26 02:57:32+00:00 [Note] [Entrypoint]: Switching to dedicated user 'mysql'
    2021-06-26 02:57:32+00:00 [Note] [Entrypoint]: Entrypoint script for MySQL Server 5.7.34-1debian10 started.
    ```
    ```sh
    $ 
    $ root@mysql:/ ps aux
    USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
    mysql        1  2.7 10.9 2625520 224000 ?      Ssl  02:57   0:07 mysqld
    root        88  0.0  0.1   3864  3292 pts/0    Ss   02:58   0:00 bash
    root       704  0.0  0.1   7636  2736 pts/0    R+   03:02   0:00 ps aux
    ```

- MySQL の docker image `mysql` での環境変数<br>
    MySQL の docker image `mysql` では、以下の環境変数が使われている
    - `MYSQL_ROOT_PASSWORD` : [必須] root ユーザーに対しての MySQL ログインパスワード
    - `MYSQL_USER` : [オプション] root ユーザー以外の新規ユーザー名。設定することで、新規ユーザーが自動的に作成される
    - `MYSQL_PASSWORD` : [オプション] 新規ユーザーに対しての MySQL ログインパスワード
    - `MYSQL_DATABASE` : [オプション] MySQL サーバー起動時に作成するデータベース名

    これらの環境変数は、`docker run` コマンド実行時のオプション引数で設定できる。<br>
    docker-compose を使用する場合は、`environment` タグで指定できる

    > MySQL サーバーの HOST と PORT を設定する環境変数は、用意されていないことに注意。HOST と PORT は、MySQL 設定ファイル `etc/my.cnf` で設定できる<br> 
    > 尚、MySQL の HOST は、デフォルトでは `localhost` になる<br>
    > また、MySQL の PORT は、デフォルトでは `3306` になる<br>

## ■ 参考サイト
- https://github.com/shibuiwilliam/ml-system-in-actions/tree/main/chapter5_operations/prediction_monitoring_pattern
- https://qiita.com/nanakenashi/items/180941699dc7ba9d0922
- 