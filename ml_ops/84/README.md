# alembic を使用して PostgreSQL　データベースの DB マイグレーションを行う

alembic は、Python の SQLAlchemy を使用しているときに DB の管理をしてくれる migration ツールである。

ここでは、alembic を使用して PostgreSQL　データベースの DB マイグレーションを行う方法を記載する

> - DB マイグレーション [DB migration]
>     DB に保存されているデータを保持したまま、テーブルの作成やカラムの変更などを行う事。


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
          - POSTGRES_DB=postgres_db   # データベース名
        command: -c 'config_file=/etc/postgresql/postgresql.conf'

    ```

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

1. alembic をインストールする<br>
    ```sh
    pip install alembic
    ```
    > alembic をインストールすれば、SQLAlchemy もインストールされることに注意

    環境によっては、psycopg2 のインストールも必要な模様
    ```sh
    pip install psycopg2
    ```

1. alembic のプロジェクトを作成する<br>
    ```sh
    alembic init ${PROJECT_NAME}
    ```

    上記コマンド実行後、以下のファイル郡が自動的に作成される
    ```sh
    ├── alembic.ini                 # alembic のスクリプトが実行される時に読まれる構成ファイル
    └── migrations
        ├── README
        ├── env.py                  # マイグレーションツールが実行された時に必ず実行される Python スクリプト（SQLAlchemyのEngineを設定や生成を行って、migration が実行できるように修正する）
        ├── script.py.mako          # 新しい migration スクリプトを生成するために使用される Mako テンプレートファイル
        └── versions                # alembic revision コマンドでマイグレーションファイルを作成した後に、migration スクリプトが保存されるディレクトリ
    ```

1. `alembic.ini` を修正する<br>
    ```ini
    [alembic]
    # path to migration scripts
    script_location = migrations
    ...
    sqlalchemy.url = postgresql://localhost:5432/postgres_db?user=postgres&password=1234
    ...
    ```

    今回は、PostgreSQL を使用するので、`sqlalchemy.url` で指定している URL を、デフォルトの `driver://user:pass@localhost/dbname` から `postgresql://localhost:5432/postgres_db?user=postgres&password=1234` に変更する
    
    > `docker-compose.yml` の環境変数で定義しているユーザー名やデータベース名に一致する URL を設定すること


1. SQLAlchemy の Python コードを作成する<br>
    SQLAlchemy を使用して、MySQL サーバーのデータベースに、CRUD 処理 [Create + Read + Update + Destory] するための Python スクリプトを作成する

    - `config.py` : MySQL の各種設定情報を定義<br>
        ```python
        # coding=utf-8
        class MySQLConfig:
            # クラス変数
            username="root"
            password="tShH78;g"
            host="localhost"
            port="3306"
            db_name="test_db"
            database_url = f"mysql+pymysql://{username}:{password}@{host}/{db_name}?charset=utf8"
        ```

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

    - `models.py` : データベース定義<br>
        ```python
        # coding=utf-8
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
        ```

    ポイントは、以下の通り

    - データベースエンジンを作成する<br>
        ```python
        # engine 作成
        engine = create_engine(
            MySQLConfig.database_url,
            encoding = "utf-8",
            echo = True               # True : 実行のたびにSQLが出力される
        )
        ```

    - モデルクラスの基底クラスを作成する<br>
        ```python
        # Base クラス（独自に定義するテーブルデータに対応するモデルクラスの基底クラス）を作成
        Base = declarative_base()

        # 予め Base クラスに query プロパティを仕込んでおく
        Base.query = session.query_property()
        ```

    - モデルクラスを作成する<br>
        ```python
        class UserData(Base):
            """
            MySQL でテーブルデータを定義したモデルクラス
            """
            __tablename__ = "userdata"
            id = Column('id', Integer, primary_key = True)
            name = Column('name', String(200))
            age = Column('age', Integer)
        ```

        > 後述のマイグレーションファイル生成を行う `alembic revision` コマンドで、このモデルクラスに応じたマイグレーションファイルが作成される

    - Session を作成する<br>
        ```python
        # Session クラス作成
        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # sessionmaker インスタンスを内包した scoped_session インスタンスを生成
        # sessionmaker との違いは、Session() を何回実行しても同一の Session が返されるという点
        session = scoped_session(Session)
        ```

    - 以下のようなスクリプトを実行することで、PosgreSQL データベースにテーブルデータを追加し、CRUD処理することができるが、今回は DB マイグレーションを行いたいだけなので、このような処理は行わないようにする
        ```sh
        # テーブルデータをデータベースに作成する
        Base.metadata.create_all(bind=engine)

        # テーブルデータへの INSERT 処理
        user_data = UserData(id=0, name="Tom", age=28)
        session.add(user_data)  
        session.commit()

        # SELECT 処理
        user_data = session.query(UserData).first()      # userテーブルの最初のレコードをクラスで返す
        users_data = session.query(UserData).all()       # userテーブルの全レコードをクラスが入った配列で返す
        ```

1. alembic が生成した `env.py` を修正する<br>
    `env.py` は、`alembic init` コマンド実行時に自動的に作成され、マイグレーションツールが実行された時に必ず実行される Python スクリプトになっているが、このスクリプトを用途に応じて修正する。
    今回のケースでは、以下の「修正箇所」の部分を修正している。

    ```python
    from logging.config import fileConfig

    from sqlalchemy import engine_from_config
    from sqlalchemy import pool

    from alembic import context
    from db.setting import Base     # 修正箇所

    # this is the Alembic Config object, which provides
    # access to the values within the .ini file in use.
    config = context.config

    # Interpret the config file for Python logging.
    # This line sets up loggers basically.
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)

    # add your model's MetaData object here
    # for 'autogenerate' support
    # from myapp import mymodel
    # target_metadata = mymodel.Base.metadata
    #target_metadata = None
    target_metadata = Base.metadata     # 修正箇所

    # other values from the config, defined by the needs of env.py,
    # can be acquired:
    # my_important_option = config.get_main_option("my_important_option")
    # ... etc.

    def run_migrations_offline():
        """Run migrations in 'offline' mode.

        This configures the context with just a URL
        and not an Engine, though an Engine is acceptable
        here as well.  By skipping the Engine creation
        we don't even need a DBAPI to be available.

        Calls to context.execute() here emit the given string to the
        script output.

        """
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()


    def run_migrations_online():
        """Run migrations in 'online' mode.

        In this scenario we need to create an Engine
        and associate a connection with the context.

        """
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        url = config.get_main_option("sqlalchemy.url")      # 修正箇所 / "sqlalchemy.url" は、alembic.ini で指定している sqlalchemy.url

        with connectable.connect() as connection:
            context.configure(
                url=url,    # 修正箇所
                connection=connection, target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()


    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
    ```

    ポイントは、以下の通り

    - SQLAlchemy でテーブルデータをデータベースに作成するには、`Base.metadata.create_all(bind=engine)` のような処理を行うが、alembic の場合は `target_metadata = Base.metadata` として、`context.configure()` の `target_metadata` 引数に渡す部分がこれに相当する処理を行っている

    - `config.get_main_option()` で `alembic.ini` から `sqlalchemy.url` の値を取得し、`context.configure()` の `url` 引数に渡している


1. SQLAlchemy モデルクラスの内容を元に migration スクリプトファイルを作成する<br>
    ```sh
    alembic revision --autogenerate -m ${MIGRATION_FILE_NAME}
    ```
    - `--autogenerate` : SQLAlchemyのモデル（`models.py` で定義している `Model` クラス）の内容を元にマイグレーションファイルを自動生成

    上記コマンドを実行することで、`${PROJECT_NAME}/versions` ディレクトリ以下に、以下のような migration スクリプトファイルが自動生成される

    - `${PROJECT_NAME}/versions/9e1d86897047_create_table.py`<br>
        ```python
        """create_table
        Revision ID: 9e1d86897047
        Revises: 
        Create Date: 2022-08-10 22:42:13.509055
        """
        from alembic import op
        import sqlalchemy as sa


        # revision identifiers, used by Alembic.
        revision = '9e1d86897047'
        down_revision = None
        branch_labels = None
        depends_on = None


        def upgrade():
            # ### commands auto generated by Alembic - please adjust! ###
            op.create_table('userdata',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=True),
            sa.Column('age', sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint('id')
            )
            # ### end Alembic commands ###


        def downgrade():
            # ### commands auto generated by Alembic - please adjust! ###
            op.drop_table('userdata')
            # ### end Alembic commands ###

        ```

1. マイグレーションスクリプトを元に DB マイグレーションを行う（PostgreSQL データベースに反映する）<br>
    ```sh
    alembic upgrade head
    ```

    上記コマンドを実行することで、先に作成した `${PROJECT_NAME}/versions/` ディレクトリ以下にある migration スクリプトファイルが実行され DB マイグレーションが行われる

1. 確認マイグレーション操作を行う<br>

    - 現在のマイグレーション状態を確認
        ```sh
        alembic current
        ```

    - マイグレーション履歴を確認<br>
        ```sh
        alembic history
        ```

    - マイグレーションの巻き戻し<br>
        ```sh
        alembic downgrade ${VERSION}
        ```

1. PostgreSQL サーバーに接続する<br>
    PostgreSQL サーバーの docker コンテナに接続した上で、`psql`　コマンドで（docker コンテナ内の）PostgreSQL サーバーに接続する
    ```sh
    docker exec -it postgresql-container /bin/bash -c "psql -h localhost -U postgres"
    ```

    > コンテナ内通信で PostgreSQL サーバーに接続するので、ホスト名は `localhost` にしている

1. PostgreSQL データベースのマイグレーションが行われているか確認する<br>

    1. データベースの一覧確認する<br>
        PostgreSQL サーバー内で以下のコマンドを実行する
        ```sh
        \l
        ```
        ```sh
                                        List of databases
            Name     |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges   
        -------------+----------+----------+------------+------------+-----------------------
        postgres    | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
        postgres_db | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
        template0   | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
                    |          |          |            |            | postgres=CTc/postgres
        template1   | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
                    |          |          |            |            | postgres=CTc/postgres
        (4 rows)
        ```

    1. 作成したデータベースに接続する<br>
        PostgreSQL サーバーに接続後、以下のコマンドを実行する
        ```sh
        \c ${DATABESE_NAME}
        ```
        ```sh
        # 例
        \c postgres_db
        ```

    1. データベースを確認する<br>
        PostgreSQL サーバー内で以下のコマンドを実行する
        ```sh
        \d
        ```
        ```sh
                    List of relations
        Schema |      Name       |   Type   |  Owner   
        --------+-----------------+----------+----------
        public | alembic_version | table    | postgres
        public | userdata        | table    | postgres
        public | userdata_id_seq | sequence | postgres
        (3 rows)
        ```

    1. テーブル構造を確認する<br>
        PostgreSQL サーバー内で以下のコマンドを実行する
        ```sh
        \d ${TABLE_NAME}
        ```
        ```sh
        # 例
        \d userdata
        ```
        ```sh
                                            Table "public.userdata"
        Column |          Type          | Collation | Nullable |               Default                
        --------+------------------------+-----------+----------+--------------------------------------
        id     | integer                |           | not null | nextval('userdata_id_seq'::regclass)
        name   | character varying(200) |           |          | 
        age    | integer                |           |          | 
        Indexes:
            "userdata_pkey" PRIMARY KEY, btree (id)
        ```

        > `models.py` のモデルクラス `UserData(Base)` で定義したテーブルデータの内容が、正常に DB マイグレーションできている

    1. PostgreSQL サーバーから exit する<br>
        PostgreSQL サーバー内で以下のコマンドを実行する
        ```sh
        \q
        ```

## ■ 参照サイト

- https://zenn.dev/shimakaze_soft/articles/4c0784d9a87751
- https://qiita.com/penpenta/items/c993243c4ceee3840f30