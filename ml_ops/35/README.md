# 【MySQL】SQLAlchemy を使用して Python スクリプトから MySQL に接続する（docker + docker-compose での構成）

## 方法

1. PyMySQL をインストールする<br>
    ```sh
    $ pip install PyMySQL
    ```

1. SQLAlchemy をインストールする<br>
    ```sh
    $ pip install sqlalchemy
    ```

1. SQLAlchemy の Python コードを作成する<br>
    SQLAlchemy を使用して、MySQL サーバーのデータベースに、CRUD 処理 [Create + Read + Update + Destory] するための Python スクリプトを作成する。
    - `config.py` : MySQL の各種設定情報を定義<br>
        ```python
        # coding=utf-8
        class MySQLConfig:
            # クラス変数
            #username="root"         # root ユーザーを使用する場合は、"root" を設定
            username="user"         # MySQL サーバーの環境変数 `MYSQL_USER` を設定して作成した新規ユーザーを使用する場合は、`MYSQL_USER` と同じ値を設定
            password="password"     # root ユーザーの場合は、MySQL サーバーの環境変数 `MYSQL_ROOT_PASSWORD` と同じ値を設定。新規ユーザーを作成する場合は、MySQL サーバーの環境変数 `MYSQL_PASSWORD` と同じ値を設定
            db_name="test_db"       # MySQL サーバーの環境変数 `MYSQL_DATABASE` を設定した場合は、`MYSQL_DATABASE` と同じ値を設定
            host="localhost"        # デフォルトでは、"localhost"
            port="3306"             # デフォルトでは、3306
            database_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}?charset=utf8"
        ```

        > 後述の `username`, `password`, `db_name` は、`docker-compose.yml` で定義する各種 MySQL 環境変数と同じ値に設定しておく

        > `host` と `port` は、MySQL サーバーのデフォルト値を設定しておく。

    - `setting.py` : SQLAlchemy での初期化処理<br>
        SQLAlchemy での初期化処理として、Engine や Session, Base クラス（独自に定義するテーブルデータに対応するモデルクラスの基底クラス）の作成を行う

        ```python
        # coding=utf-8
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, scoped_session
        from sqlalchemy.ext.declarative import declarative_base

        from config import MySQLConfig

        # engine 作成
        engine = create_engine(
            MySQLConfig.database_url,
            encoding = "utf-8",
            echo = True               # True : 実行のたびにSQLが出力される
        )

        # Session クラス作成
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # sessionmaker インスタンスを内包した scoped_session インスタンスを生成
        # sessionmaker との違いは、Session() を何回実行しても同一の Session が返されるという点
        session = scoped_session(Session)

        # Base クラス（独自に定義するテーブルデータに対応するモデルクラスの基底クラス）を作成
        Base = declarative_base()

        # 予め Base クラスに query プロパティを仕込んでおく
        Base.query = session.query_property()
        ```

    - `crud.py` : MySQL サーバーのデータベースへの CRUD 処理
        ```python
        # coding=utf-8
        import os
        import argparse
        from sqlalchemy import Column, Integer, String, Float, DateTime
        from setting import engine, session, Base

        class UserData(Base):
            """
            MySQL でテーブルデータを定義したモデルクラス
            """
            __tablename__ = "userdata"
            id = Column('id', Integer, primary_key = True)
            name = Column('name', String(200))
            age = Column('age', Integer)

        if __name__ == "__main__":
            parser = argparse.ArgumentParser()
            parser.add_argument('--debug', action='store_true', help="デバッグモード有効化")
            args = parser.parse_args()
            if( args.debug ):
                for key, value in vars(args).items():
                    print('%s: %s' % (str(key), str(value)))

            # テーブルデータをデータベースに作成する
            Base.metadata.create_all(bind=engine)

            # テーブルデータへの INSERT 処理
            user_data = UserData(id=0, name="Tom", age=28)
            session.add(user_data)  
            session.commit()

            # SELECT 処理
            user_data = session.query(UserData).first()      # userテーブルの最初のレコードをクラスで返す
            users_data = session.query(UserData).all()       # userテーブルの全レコードをクラスが入った配列で返す
            print( "[user_data] __tablename__={}, id={}, name={}, age={}".format(user_data.__tablename__, user_data.id, user_data.name, user_data.age) )
            for i, user_data in enumerate(users_data):
                print( "[users_data {}] __tablename__={}, id={}, name={}, age={}".format(i, user_data.__tablename__, user_data.id, user_data.name, user_data.age) )        
        ```


1. MySQL サーバーの設定ファイル `my.cnf` を作成する<br>
    例えば、以下のような MySQL サーバーの設定ファイル `my.cnf` を作成し、`mysql/my.cnf` 以下に保存する
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
    version: '2.3'

    services:
      mysql-server:
        container_name: mysql-container
        image: mysql:5.7
        #image: mysql:latest
        ports:
          - "3306:3306"
        tty: true
        volumes:
          - ${PWD}/mysql/my.cnf:/etc/my.cnf                         # 作成した MySQL の設定ファイル `my.cnf` を `mysql:latest` の設定ファイル `/etc/my.cnf` にマウントして差し替える
          - ${PWD}/mysql/db/data:/var/lib/mysql                     # MySQL のデータが保存されているディレクトリ `/var/lib/mysql` をローカルディレクトリにマウント
          - ${PWD}/mysql/db/initdb.d:/docker-entrypoint-initdb.d    # 
        restart: always                                             # 終了ステータスが異常の場合も常に再起動
        stdin_open: true                                            # コンテナの標準入力をオープンしたままにする。`docker run` での `-i` オプションに対応
        environment:                                                # MySQL の docker image `mysql` で使用される環境変数を追加
          TZ: "Asia/Tokyo"
          LC_ALL: C.UTF-8
          LANG: C.UTF-8
          MYSQL_ROOT_PASSWORD: password                             # [必須] root ユーザーに対しての MySQL ログインパスワード
          MYSQL_USER: user                                          # [オプション] MySQL サーバー起動時に作成するデータベース名
          MYSQL_PASSWORD: password                                  # [オプション] 新規ユーザーに対しての MySQL ログインパスワード            
          MYSQL_DATABASE: "test_db"                                 # [オプション] MySQL サーバー起動時に作成するデータベース名
    ```

    ポイントは、以下の通り<br>
    - `volumes` タグで、作成した設定ファイル `mysql/my.cnf` を `/etc/my.cnf` にマウント<br>
        MySQL docker image `mysql` では、`/etc/my.cnf` にある設定ファイルで MySQL サーバーが起動されるので、作成した設定ファイル `mysql/my.cnf` をこのディレクトリにマウントし、設定ファイルが反映させるようにする

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
    $ sleep 5
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

    1. ユーザー名とホスト名の確認<br>
        MySQL サーバーに接続した状態で、以下のコマンドを実行することで、MySQL のユーザー名とホスト名が確認できる。
        ```sh
        mysql>  SELECT USER();
        ```
        ```sh
        +----------------+
        | USER()         |
        +----------------+
        | user@localhost |
        +----------------+
        1 row in set (0.01 sec)
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
        ```sh
        # Copyright (c) 2016, 2021, Oracle and/or its affiliates.
        #
        # This program is free software; you can redistribute it and/or modify
        # it under the terms of the GNU General Public License, version 2.0,
        # as published by the Free Software Foundation.
        #
        # This program is also distributed with certain software (including
        # but not limited to OpenSSL) that is licensed under separate terms,
        # as designated in a particular file or component or in included license
        # documentation.  The authors of MySQL hereby grant you an additional
        # permission to link the program and your derivative works with the
        # separately licensed software that they have included with MySQL.
        #
        # This program is distributed in the hope that it will be useful,
        # but WITHOUT ANY WARRANTY; without even the implied warranty of
        # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        # GNU General Public License, version 2.0, for more details.
        #
        # You should have received a copy of the GNU General Public License
        # along with this program; if not, write to the Free Software
        # Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

        !includedir /etc/mysql/conf.d/
        !includedir /etc/mysql/mysql.conf.d/
        ```
    - `/var/lib/mysql` : MySQL のデータ（データベース等）が保存されるディレクトリ
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