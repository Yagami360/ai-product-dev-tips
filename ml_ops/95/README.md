# Elixir 言語において Phoenix 版 Ecto の Ecto.Schema で定義したテーブルデータの内容を PostgreSQL データベースのテーブルに追加する

Ecto は、Elixer における各種データベース（PostgreSQL や MySQL など。デフォルトは PostgreSQL）の操作を共通のインターフェイスで操作可能なラッパーライブラリである。

Ecto は大きくわけて以下の4つの構成要素から構成される。

- Ecto.Repo<br>
  data store のラッパーで、データストアに対するAPIを提供する。
  Ecto では Repository (Repo) を通してデータベースの CRUD 処理を行う。

- Ecto.Schema<br>
  Ecto におけるテーブルデータは、Schema と呼ばれる構造体（テーブル）で定義するが、この Schema（構造体/テーブル）の内容を PosgreSQL DB に反映したりする際に使用される。

- Ecto.Changeset<br>
  PosgreSQL データベースのテーブルデータの一部の列のみを変更する処理（changeset）などで使用する

- Ecto.Query<br>
  データベースへの問い合わせは、まず Query を構築してから、次に Ecto.Repo に Query を渡してデータベースへの問い合わせを実行する、というステップを踏む


「[Elixir 言語において Ecto の Ecto.Schema で定義したテーブルデータの内容を PostgreSQL データベースに反映する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/93)」では、オリジナルの Ecto の Ecto.Schema を使用して、テーブルデータ（Schema）を PosgreSQL データベースに反映する方法を記載したが、ここでは、
ここでは、Phoenix にインストール済みの Ecto の Ecto.Schema を使用して、テーブルデータ（Schema）を PosgreSQL データベースのテーブルに反映する方法を記載する

## ■ 方法

1. PosgreSQL サーバーを起動する<br>
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
              - POSTGRES_PASSWORD=postgres    # sudo ユーザのパスワード
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
        rm -rf postgresql/db
        mkdir -p postgresql/db
        docker-compose -f docker-compose.yml stop
        docker-compose -f docker-compose.yml up -d
        ```

1. Elixir をインストールする<br>
    - MacOS の場合<br>
        ```sh
        brew install elixir
        ```

    - Ubuntu の場合<br>
        ```sh
        # Erlang をインストール
        wget https://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb && sudo dpkg -i erlang-solutions_1.0_all.deb
        sudo apt-get update
        sudo apt-get install esl-erlang

        # elixir をインストール
        sudo apt-get install elixir
        ```

    > Elixir をインストールすることで、`mix` コマンドが使えるようになる。`mix` コマンドは、コンパイル＆テスト＆特定のコマンド実行などを複合的に行うコマンドで、以下のようなコマンドがある
    > - `mix new ${PROJECT_NAME}` : プロジェクトを作成する<br>
    >     ※ ここでいうプロジェクトとは、`mix.exs` という名前のファイルに配置されたモジュール
    > - `mix compile` : プロジェクトのコンパイルを行う<br>
    > - `mix test` : プロジェクトのテストを実行<br>
    > - `mix run` : プロジェクト内の特定のコマンドを実行<br>
    > - `mix do コマンド１, コマンド２` : カンマで区切られたコマンドを順次実行する（コマンド１を実行したあとコマンド２を実行するといった具合）<br>

1. Node.js をインストールする<br>
    phoenix では、アセットファイルのコンパイルに node.js 製ツールを使用するので、node.js もインストールする
    - MacOS の場合
        ```sh
        brew install node
        ```

    - Ubuntu の場合<br>
        ```sh
        sudo apt update
        sudo apt install nodejs
        sudo apt install npm
        ```

1. Phoenix をインストールする<br>
    ```sh
    # hex をインストール
    mix local.hex --force

    # Phoenix インストールする
    mix archive.install hex phx_new --force

    # Phoenix のバージョン確認
    mix phx.new -v
    ```
    - `--force` : インストール時の yes or no の追加入力なしにする

1. Elixir の Phoenix プロジェクトを作成する
    ```sh
    mix phx.new ${PROJECT_NAME}
    ```

    > 最近の Phoenix バージョンでは、Phoenix 実行コマンドが `mix phoenix` -> `mix phx` になっていることに注意

    プロジェクト作成後、以下のようなディレクトリ構成でのプロジェクトフォルダが自動的に作成される<br>

    <img width="280" alt="image" src="https://user-images.githubusercontent.com/25688193/187032730-c61fa8e3-101a-4807-bdbe-b0b972c97cb7.png">

    Ecto に関連するのは、この内、Ecto.Repo モジュールを定義した `lib/${PROJECT_NAME}/repo.ex` と、そのコンフィグ情報を定義した `config/config.exs`, `config/dev.exs`, `config/prod.exs` である。

    > オリジナルの Ecto の場合でも、`mix ecto.gen.repo` コマンドでプロジェクト作成時に、`lib/${PROJECT_NAME}/repo.ex` と、そのコンフィグ情報を定義した `config/config.exs` が自動的に作成されていたが、Phoenix 組み込み版 Ecto の場合もこれと同じになる

    > オリジナルの Ecto の場合は、`application.ex` を修正する必要もあったが、Phoenix 組み込み版 Ecto の場合は必要ない

1. Ecto.Repo のコンフィグ情報を定義した `config/config.exs`, `config/dev.exs`, `config/prod.exs` を確認 or 修正する<br>
    今回は、開発版で動作テストするので、`config/dev.exs` を確認する。特に以下の部分の設定値が重要
    ```ex
    import Config

    # Configure your database
    config :elixir_phoenix_ecto, ElixirPhoenixEcto.Repo,
      username: "postgres",
      password: "postgres",
      hostname: "localhost",
      database: "elixir_phoenix_ecto_dev",
      stacktrace: true,
      show_sensitive_data_on_connection_error: true,
      pool_size: 10
    ...
    ```
    `username`, `password`, `hostname` は、PosgreSQL サーバーの docker-compose で定義した値と一致させる必要がある。
    またデータベース名は、デフォルトでは `${PROJECT_NAME}_dev` になるので、変更したい場合は、ここの値を変更すればよい

1. PosgreSQL サーバーにデータベースを作成する<br>
    以下のコマンドを実行することで、PosgreSQL サーバー内に PosgreSQL DB が作成される。このときの DB 名は、`config/dev.exs` の `database` で指定したデータベース名になる
    ```sh
    cd ${PROJECT_NAME}
    mix ecto.create
    ```

1. PosgreSQL サーバーのデータベースにテーブルを作成する<br>
    1. マイグレーションファイルを作成する<br>
        以下のコマンドを実行することで、`priv/repo/migrations` ディレクトリ以下に、空のマイグレーションファイルが作成される
        ```sh
        cd ${PROJECT_NAME}
        mix ecto.gen.migration ${MIGRATION_NAME}
        ```

        > DB マイグレーション [DB migration] : DB に保存されているデータを保持したまま、テーブルの作成やカラムの変更などを行う事。

        > マイグレーションファイル : DB マイグレーションの処理内容を定義したスクリプトファイル

        - `priv/repo/migrations/xxxxxx_${MIGRATION_NAME}.exs`
            ```ex
            defmodule ElixirEctoPostgresql.Repo.Migrations.CreatePersonTableMigration do
              use Ecto.Migration

              def change do

              end
            end
            ```

            - `def change` にマイグレーション処理を定義する

    1. マイグレーションファイルを修正する<br>
        上記で作成されたマイグレーションファイル `priv/repo/migrations/xxxxxx_${MIGRATION_NAME}.exs` を修正する
        ```sh
        defmodule elixir_ecto_postgresql.Repo.Migrations.CreatePersonTableMigration do
          use Ecto.Migration

          def change do
            create table(:person_table) do
              add :name, :string
              add :age, :integer
            end
          end
        end
        ```

        - `person_table` の部分は、DB に追加するテーブル名

    1. マイグレーションを実行し、PostgreSQL データベース内にテーブルを作成する
        マイグレーションファイルに、テーブルデータを作成する `create table` を定義しているので、マイグレーションを実行することにより、PostgreSQL データベースにテーブルデータを作成することができる
        ```sh
        mix ecto.migrate
        ```

1. Schema を定義したスクリプトを作成する<br>
    Schema を定義した `lib/${PROJECT_NAME}/person_schema.ex` を作成する
    ```ex
    defmodule ElixirPhoenixEcto.PersonSchema do
      # `use Ecto.Schema` で、Ecto.Schema を再定義することで、独自の Schema 定義を行っている
      use Ecto.Schema

      # PosgreSQL DB のテーブルに反映するためのテーブル定義
      schema "person_table" do
        field :name, :string
        field :age, :integer
      end
    end
    ```

    ポイントは、以下の通り

    - `use Ecto.Schema` で、Ecto.Schema を再定義することで、独自の Schema 定義を行っている

    - `schema ${TABLE_ANME} do ... end` の部分で、PosgreSQL DB のテーブルに反映する要素値の定義を行っている

1. Elixir shell を起動する
    ```sh
    cd ${PROJECT_NAME}
    iex -S mix
    ```

1. 作成した Schema を PosgreSQL DB に反映する。<br>
    Elixir shell 内にて、以下の Elixer スクリプトを実行する
    ```sh
    # Schema オブジェクト作成
    person1 = %ElixirPhoenixEcto.PersonSchema{name: "Yagami", age: 28}
    person2 = %ElixirPhoenixEcto.PersonSchema{name: "Yagoo", age: 30}

    # PosgreSQL DB のテーブルに schema の内容を insert
    ElixirPhoenixEcto.Repo.insert(person1)
    ElixirPhoenixEcto.Repo.insert(person2)
    ```

    Ecto.Schema で定義したテーブルデータの内容を PosgreSQL データベースのテーブルに反映する処理の流れは、以下のようになる

    1. Ecto.Schema を use した Schema モジュール内で `schema xxx do .. end` を定義
    1. このモジュールに対する Schema オブジェクトを作成
    1. Ecto.Repo の `insert()` 関数に、この Schema オブジェクトを指定し、Schema オブジェクトの内容を PosgreSQL データベースのテーブルに反映する

1. PosgreSQL サーバーにログインしてデータベースとテーブルが作成されていることを確認する
    ```sh
    # PosgreSQL サーバーにログイン
    docker exec -it postgresql-container /bin/bash -c "psql -h localhost -U postgres"
    ```

    PostgreSQL サーバーに接続後、以下のコマンドを実行する
    ```sh
    # データベースの一覧確認する
    \l
    ```
    ```sh
                                            List of databases
              Name           |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges   
    -------------------------+----------+----------+------------+------------+-----------------------
    elixir_phoenix_ecto_dev | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
    postgres                | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
    template0               | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
                            |          |          |            |            | postgres=CTc/postgres
    template1               | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
                            |          |          |            |            | postgres=CTc/postgres
    ```
    > `mix ecto.create` コマンドで DB `elixir_phoenix_ecto_dev` がうまく作成されている

    ```sh
    # データベースに接続する
    \c ${DATABESE_NAME}
    ```

    データベースに接続後、以下のコマンドを実行する
    ```sh
    # データベースを確認する
    \d
    ```
    ```sh
                    List of relations
    Schema |        Name         |   Type   |  Owner   
    --------+---------------------+----------+----------
    public | person_table        | table    | postgres
    public | person_table_id_seq | sequence | postgres
    public | schema_migrations   | table    | postgres
    ```
    > マイグレーションにより、データベース内にテーブル `person_table` がうまく作成されている

    テーブルの中身を確認する
    ```sh
    \d person_table
    ```
    ```sh
                                        Table "public.person_table"
    Column |          Type          | Collation | Nullable |                 Default                  
    --------+------------------------+-----------+----------+------------------------------------------
    id     | bigint                 |           | not null | nextval('person_table_id_seq'::regclass)
    name   | character varying(255) |           |          | 
    age    | integer                |           |          | 
    Indexes:
        "person_table_pkey" PRIMARY KEY, btree (id)
    ```
    > マイグレーションファイル内で定義したテーブル定義で、うまく作成できている

    以下のコマンドを実行し、テーブルの各要素の値を確認する
    ```sh
    select name from person_table;
    ```
    ```sh
      name  
    --------
      Yagami
      Yagoo
    (2 rows)
    ```
    ```sh
    select age from person_table;
    ```
    ```sh
      age  
    --------
      28
      30
    (2 rows)
    ```

    > Schcma で定義したテーブルの値がうまく追加されている

## ■ 参考サイト

- https://qiita.com/sand/items/71d0b35d74a4781f3564#%EF%BC%94ectoschema
- https://zenn.dev/koga1020/books/phoenix-guide-ja-1-5/viewer/ecto#%E3%82%B9%E3%82%AD%E3%83%BC%E3%83%9E