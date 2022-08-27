# Elixer 言語において Ecto の Ecto.Repo を使用して PostgreSQL データベースの CRUD 処理を行う

Ecto は、Elixer における各種データベース（PostgreSQL や MySQL など。デフォルトは PostgreSQL）の操作を共通のインターフェイスで操作可能なラッパーライブラリである。

Ecto は大きくわけて以下の4つの構成要素から構成される。

- Ecto.Repo<br>
  data store のラッパーで、データストアに対するAPIを提供する。
  Ecto では Repository (Repo) を通してデータベースの CRUD 処理を行う。

- Ecto.Schema<br>
  DB テーブルを Elixir の構造体に map するために使わわれる

- Ecto.Changeset<br>
  外部データである parameters をもとにデータベースに変更を加える時に用いられる変更部分（params）を表すデータ構造

- Ecto.Query<br>
  データベースへの問い合わせは、まず Query を構築してから、次に Ecto.Repo に Query を渡してデータベースへの問い合わせを実行する、というステップを踏む

ここでは、Ecto の Ecto.Repo を使用して、PostgreSQL データベースの CRUD 処理を行う方法を記載する

## ■ ToDo

- [ ] `mix ecto.create` コマンドでデータベース作成時に、以下のエラーが発生する問題の解決
  ```sh
  21:59:55.967 [error] GenServer #PID<0.203.0> terminating
  ** (RuntimeError) Connect raised a FunctionClauseError error. The exception details are hidden, as
  they may contain sensitive data such as database credentials.

      (postgrex 0.13.5) lib/postgrex/messages.ex:371: Postgrex.Messages.decode_auth_type/1
      (postgrex 0.13.5) lib/postgrex/messages.ex:64: Postgrex.Messages.parse/3
      (postgrex 0.13.5) lib/postgrex/protocol.ex:2004: Postgrex.Protocol.msg_decode/1
      (postgrex 0.13.5) lib/postgrex/protocol.ex:1978: Postgrex.Protocol.msg_recv/3
      (postgrex 0.13.5) lib/postgrex/protocol.ex:589: Postgrex.Protocol.auth_recv/3
      (postgrex 0.13.5) lib/postgrex/protocol.ex:504: Postgrex.Protocol.handshake/2
      (db_connection 1.1.3) lib/db_connection/connection.ex:135: DBConnection.Connection.connect/2
      (connection 1.0.4) lib/connection.ex:622: Connection.enter_connect/5
  Last message: nil
  State: Postgrex.Protocol
  ** (Mix) The database for ElixirEctoPostgresql.Repo couldn't be created: an exception was raised:
      ** (RuntimeError) Connect raised a FunctionClauseError error. The exception details are hidden, as
  they may contain sensitive data such as database credentials.

          (postgrex 0.13.5) lib/postgrex/messages.ex:371: Postgrex.Messages.decode_auth_type/1
          (postgrex 0.13.5) lib/postgrex/messages.ex:64: Postgrex.Messages.parse/3
          (postgrex 0.13.5) lib/postgrex/protocol.ex:2004: Postgrex.Protocol.msg_decode/1
          (postgrex 0.13.5) lib/postgrex/protocol.ex:1978: Postgrex.Protocol.msg_recv/3
          (postgrex 0.13.5) lib/postgrex/protocol.ex:589: Postgrex.Protocol.auth_recv/3
          (postgrex 0.13.5) lib/postgrex/protocol.ex:504: Postgrex.Protocol.handshake/2
          (db_connection 1.1.3) lib/db_connection/connection.ex:135: DBConnection.Connection.connect/2
          (connection 1.0.4) lib/connection.ex:622: Connection.enter_connect/5
  ```


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
    
    - MacOS の場合<br>
      ```sh
      brew install node
      ```

    - Ubuntu の場合<br>
      ```sh
      sudo apt update
      sudo apt install nodejs
      sudo apt install npm
      ```

1. Elixir プロジェクトを作成する
    ```sh
    mix new ${PROJECT_NAME} --sup
    ```
    - `--sup` : supervision tree ありでプロジェクトを作成する

    プロジェクト作成後、以下のようなディレクトリ構成でのプロジェクトフォルダが自動的に作成される<br>
    <img width="301" alt="image" src="https://user-images.githubusercontent.com/25688193/185727617-16e4da8f-b5c3-4fe7-afce-15263e4573ef.png">

    supervision tree ありでプロジェクトを作成すると、`lib/${PROJECT_NAME}/application.ex` も作成される

    > - supervision tree<br>
    >    Supervisor と process の関係性（詳細は、https://kazucocoa.wordpress.com/2015/08/12/elixir-in-actionsupervision-tree-%E3%83%8D%E3%82%B9%E3%83%88%E3%81%95%E3%82%8C%E3%81%9Fsupervisor/ 参照）

    > - Supervisor<br>
    >     処理を行う worker process を監視するもの（詳細は、https://kazucocoa.wordpress.com/2015/08/11/elixir-in-actionfault-tolerance%E3%82%92%E4%BF%9D%E3%81%A4%E3%81%9F%E3%82%81%E3%81%AE%E7%89%B9%E5%88%A5%E3%81%AA%E8%B2%AC%E5%8B%99%E3%82%92%E8%B2%A0%E3%81%86processsupervisor/ 参照）<br>

1. `mix.exe` を修正する<br>
    `mix.exe` の `defp deps` に部分を以下のように修正する
    ```sh
    defp deps do
      [{:ecto, "~> 2.0"},
      {:postgrex, "~> 0.11"}]
    end
    ```

    > Elixir の Mix におけるプロジェクトとは、`mix.exs` という名前のファイルに配置されたモジュールで `Mix.Project` を使用して定義する。プロジェクトにインストールする各種ライブラリは、このモジュールの `defp xxx do ... end` の部分に記載する<br>

1. プロジェクトの各種ライブラリ（Ecto, PostgreSQL）をインストールする
    ```sh
    mix deps.get
    ```

    > deps ディレクトリ以下に各種ライブラリがインストールされｒｙ

1. Repo モジュールと config を作成する<br>
    以下のコマンドを実行することで、Repo モジュールを定義した `lib/${PROJECT_NAME}/repo.ex` と、そのコンフィグ情報を定義した `config/config.exs` が自動的に作成される。
    ```sh
    mix ecto.gen.repo -r ${ECTO_REPO_NAME}.Repo
    ```
    > `${ECTO_REPO_NAME}` は、`ElixirEctoPostgresql` のように Elixer 構文の `defmodule` でのモジュール名（先頭大文字）である必要があることに注意

    > Phoenix を使用した場合は、`mix phx.new` コマンドでプロジェクト作成時に、`config.exe` や `repo.ex` が自動的に作らているので、これらのファイルに後述のコードを追加していく形になる

    <img width="300" alt="image" src="https://user-images.githubusercontent.com/25688193/185728640-439b79c4-c114-4631-b940-a00d77e9dc88.png">

    - `lib/${PROJECT_NAME}/repo.ex`
      ```sh
      defmodule ElixirEctoPostgresql.Repo do
        use Ecto.Repo, 
          otp_app: :elixir_ecto_postgresql
      end
      ```

      - `use Ecto.Repo` の部分では、`use` 構文を使用して `Ecto.Repo` モジュールの `otp_app` の値を再定義している。

  	    > `use` 構文は、他のモジュールを利用して現在のモジュールの定義を変更することができる Elixler 構文

      - `otp_app` は、`Ecto.Repo` モジュール内で定義されている変数で、どのアプリがデータベースへアクセスしているかを明示している。`use` 構文で `otp_app` の値を `:elixir_ecto_postgresql` に再定義しているので、`config.exs` 内 の `config :elixir_ecto_postgresql` が設定される

    - `config/config.exs`
      ```ex
      use Mix.Config

      config :elixir_ecto_postgresql, ElixirEctoPostgresql.Repo,
        adapter: Ecto.Adapters.Postgres,
        database: "elixir_ecto_postgresql_repo",
        username: "user",
        password: "pass",
        hostname: "localhost"
      ```

      > `use` 構文は、他のモジュールを利用して現在のモジュールの定義を変更することができる

1. `lib/${PROJECT_NAME}/application.ex` を修正する<br>
    ```ex
    defmodule ElixirEctoPostgresql.Application do
      # See https://hexdocs.pm/elixir/Application.html
      # for more information on OTP Applications
      @moduledoc false

      use Application

      @impl true
      def start(_type, _args) do
        children = [
          # Starts a worker by calling: ElixirEctoPostgresql.Worker.start_link(arg)
          # {ElixirEctoPostgresql.Worker, arg}
          ElixirEctoPostgresql.Repo,
        ]

        # See https://hexdocs.pm/elixir/Supervisor.html
        # for other strategies and supported options
        opts = [strategy: :one_for_one, name: ElixirEctoPostgresql.Supervisor]
        Supervisor.start_link(children, opts)
      end
    end
    ```

    ポイントは、以下の通り

    - `application.ex` は、`mix new` コマンドでプロジェクト作成時に `--sup` オプションを有効化することで自動的に作成されるファイル

    - `ElixirEctoPostgresql.Repo` を application の supervision treeの 中の supervisor としてセットすることで、Ecto process を起動して、アプリの query を受け取り実行できるようになる？

    > - supervision tree<br>
    >    Supervisor と process の関係性（詳細は、https://kazucocoa.wordpress.com/2015/08/12/elixir-in-actionsupervision-tree-%E3%83%8D%E3%82%B9%E3%83%88%E3%81%95%E3%82%8C%E3%81%9Fsupervisor/ 参照）

    > - Supervisor<br>
    >     処理を行う worker process を監視するもの（詳細は、https://kazucocoa.wordpress.com/2015/08/11/elixir-in-actionfault-tolerance%E3%82%92%E4%BF%9D%E3%81%A4%E3%81%9F%E3%82%81%E3%81%AE%E7%89%B9%E5%88%A5%E3%81%AA%E8%B2%AC%E5%8B%99%E3%82%92%E8%B2%A0%E3%81%86processsupervisor/ 参照）<br>

1. `config/config.exs` を修正する<br>
    自身の環境に合わせて、コンフィグ情報を定義した `config/config.exs` を修正する
    ```ex
    use Mix.Config

    config :elixir_ecto_postgresql, :"Elixir.elixir_ecto_postgresql.Repo",
      adapter: Ecto.Adapters.Postgres,
      database: "elixir_ecto_postgresql_repo",
      username: "postgres",
      password: "1234",
      hostname: "localhost"

    config :elixir_ecto_postgresql, ecto_repos: [ElixirEctoPostgresql.Repo]
    ```

    ポイントは、以下の通り

    - `username`, `password`, `hostname` の値を `docker-compose.yml` で定義した PostgreSQL サーバーの設定値に合わせている

    - `application.ex` の内容に応じて、`config :elixir_ecto_postgresql, ecto_repos: [ElixirEctoPostgresql.Repo]` を追加している

      > この行を追加していないと、以下のようなエラーがでる
      > ```sh
      > warning: use Mix.Config is deprecated. Use the Config module instead
      >   config/config.exs:1
      > 
      > warning: could not find Ecto repos in any of the apps: [:elixir_ecto_postgresql].
      > 
      > You can avoid this warning by passing the -r flag or by setting the
      > repositories managed by those applications in your config/config.exs:
      > 
      >     config :elixir_ecto_postgresql, ecto_repos: [...]
      > ```

1. PostgreSQL データベースを作成する<br>
    ```sh
    mix ecto.create
    ```

    - [Todo] 上記コマンド実行時に以下のエラーがでてデータベースが作成できないので、これを解決する

      ```sh
      21:59:55.967 [error] GenServer #PID<0.203.0> terminating
      ** (RuntimeError) Connect raised a FunctionClauseError error. The exception details are hidden, as
      they may contain sensitive data such as database credentials.

          (postgrex 0.13.5) lib/postgrex/messages.ex:371: Postgrex.Messages.decode_auth_type/1
          (postgrex 0.13.5) lib/postgrex/messages.ex:64: Postgrex.Messages.parse/3
          (postgrex 0.13.5) lib/postgrex/protocol.ex:2004: Postgrex.Protocol.msg_decode/1
          (postgrex 0.13.5) lib/postgrex/protocol.ex:1978: Postgrex.Protocol.msg_recv/3
          (postgrex 0.13.5) lib/postgrex/protocol.ex:589: Postgrex.Protocol.auth_recv/3
          (postgrex 0.13.5) lib/postgrex/protocol.ex:504: Postgrex.Protocol.handshake/2
          (db_connection 1.1.3) lib/db_connection/connection.ex:135: DBConnection.Connection.connect/2
          (connection 1.0.4) lib/connection.ex:622: Connection.enter_connect/5
      Last message: nil
      State: Postgrex.Protocol
      ** (Mix) The database for ElixirEctoPostgresql.Repo couldn't be created: an exception was raised:
          ** (RuntimeError) Connect raised a FunctionClauseError error. The exception details are hidden, as
      they may contain sensitive data such as database credentials.

              (postgrex 0.13.5) lib/postgrex/messages.ex:371: Postgrex.Messages.decode_auth_type/1
              (postgrex 0.13.5) lib/postgrex/messages.ex:64: Postgrex.Messages.parse/3
              (postgrex 0.13.5) lib/postgrex/protocol.ex:2004: Postgrex.Protocol.msg_decode/1
              (postgrex 0.13.5) lib/postgrex/protocol.ex:1978: Postgrex.Protocol.msg_recv/3
              (postgrex 0.13.5) lib/postgrex/protocol.ex:589: Postgrex.Protocol.auth_recv/3
              (postgrex 0.13.5) lib/postgrex/protocol.ex:504: Postgrex.Protocol.handshake/2
              (db_connection 1.1.3) lib/db_connection/connection.ex:135: DBConnection.Connection.connect/2
              (connection 1.0.4) lib/connection.ex:622: Connection.enter_connect/5
      ```
      
1. マイグレーションファイルを作成する<br>
    以下のコマンドを実行することで、`priv/repo/migrations` ディレクトリ以下に、マイグレーションファイルが作成される
    ```sh
    mix ecto.gen.migration ${MIGRATION_NAME}
    ```

    > DB マイグレーション [DB migration] : DB に保存されているデータを保持したまま、テーブルの作成やカラムの変更などを行う事。

    > マイグレーションファイル : DB マイグレーションの処理内容を定義したスクリプトファイル

    - `priv/repo/migrations/xxxxxx_${MIGRATION_NAME}.exs`
        ```ex
        defmodule ElixirEctoPostgresql.Repo.Migrations.CreatePersonMigration do
          use Ecto.Migration

          def change do

          end
        end
        ```

        - `def change` にマイグレーション処理を定義する

1. マイグレーションファイルを修正する<br>
    上記で作成されたマイグレーションファイル `priv/repo/migrations/xxxxxx_${MIGRATION_NAME}.exs` を修正する
    ```sh
    defmodule elixir_ecto_postgresql.Repo.Migrations.CreatePersonMigration do
      use Ecto.Migration

      def change do
        create table(:person_schema) do
          add :name, :string
          add :age, :integer
        end
      end
    end
    ```

    - `person_table` の部分は、テーブル名

1. マイグレーションを実行し、PostgreSQL データベース内にテーブルを作成する
    マイグレーションファイルに、テーブルデータを作成する `create table` を定義しているので、マイグレーションを実行することにより、PostgreSQL データベースにテーブルデータを作成することができる
    ```sh
    mix ecto.migrate
    ```

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
    # データベースに接続する
    \c ${DATABESE_NAME}
    ```

    データベースに接続後、以下のコマンドを実行する
    ```sh
    # データベースを確認する
    \d
    ```

## ■ 参考サイト

- https://qiita.com/sand/items/71d0b35d74a4781f3564
- https://elixirschool.com/ja/lessons/ecto/basics
- https://qiita.com/torifukukaiou/items/bfbe459979172ecab7d9