# Elixir 言語で Phoenix を使用して簡単な REST API を作成する

## ■ 方法

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

    <img width="300" alt="image" src="https://user-images.githubusercontent.com/25688193/184292726-ef5c198f-3292-4427-bbd2-25c52df24d55.png">

    - `${PROJECT_NAME}/mix.exs`<br>
        Elixir の Mix におけるプロジェクトとは、`mix.exs` という名前のファイルに配置されたモジュールで `Mix.Project` を使用して定義する。<br>
        ```ex
        defmodule ElixirPhoenixApi.MixProject do
            use Mix.Project

            def project do
                [
                    app: :elixir_phoenix_api,
                    version: "0.1.0",
                    elixir: "~> 1.12",
                    elixirc_paths: elixirc_paths(Mix.env()),
                    compilers: [:gettext] ++ Mix.compilers(),
                    start_permanent: Mix.env() == :prod,
                    aliases: aliases(),
                    deps: deps()
                ]
            end
            ...
        ```

    - `${PROJECT_NAME}/lib/${PROJECT_NAME}_web/router.ex`<br>
        API のエンドポイントを定義している部分（ルーター）
        ```ex
        defmodule ElixirPhoenixApiWeb.Router do
            use ElixirPhoenixApiWeb, :router
            ...

            # "http:${IP_ADDRESS}:${PORT}/" のエンドポイント定義
            scope "/", ElixirPhoenixApiWeb do
                pipe_through :browser

                get "/", PageController, :index
            end

            # Other scopes may use custom stacks.
            # scope "/api", ElixirPhoenixApiWeb do
            #   pipe_through :api
            # end
            ...
        end
        ```

1. `${PROJECT_NAME}/lib/elixir_phoenix_api_web/router.ex` の API のコード（ルーター）を修正する<br>
    ```ex
    ```

    ポイントは、以下の通り

    - `use ElixirPhoenixApiWeb, :router` 部分では、`use` 構文を使用して、ルーティングするためのマクロ `ElixirPhoenixApiWeb` を定義している？

        > `:router` の部分は、アトムと呼ばれる、定数名が自身の値を表わしている定数である。アトムは、`:${アトム名}` という形式で定義する

    - `pipelines :${PIPELINE_NAME} do ... end` の部分では、各種エンドポイント呼び出し時の共通処理を定義している。定義した pipeline は、各種エンドポイント定義内 `scope "/xxx", ElixirPhoenixApiWeb do ... end` にて、`pipe_through :${PIPELINE_NAME}` のようにしてすべて実行される
        > `pipe_through` 構文は、`pipelines` 内で定義した `plug` 関数をすべて実行する構文

    - `get "/", PageController, :index` のように、`get/post ${エンドポイントアドレス}, ${コントローラー名}, ${アトム名}` の形式で GET method や POST method を定義する。<br>

        - ここで参照している各種コントローラーは、`lib/elixir_phoenix_api_web/controllers` ディレクトリ以下のコードで定義している。
            ```sh
            defmodule ElixirPhoenixApiWeb.PageController do
                use ElixirPhoenixApiWeb, :controller

                def index(conn, _params) do
                    render(conn, "index.html")
                end
            end        
            ```

            > `:index` も、この `PageController` 内で定義されたメソッド名になっている

    - 今回は、`api/health` のエンドポイントアクセス時の処理を追加するために、以下のコードを追加している

        - `router.ex`<br>
            ```ex
            # /api アクセス時のエンドポイント定義
            scope "/api", ElixirPhoenixApiWeb do
                # ルートアクセス時（http:${IP_ADDRESS}:${PORT}/）以外のエンドポイントアクセス時の共通処理を定義した pipeline 内の plug 関数を全て実行
                pipe_through :api

                # GET method
                get "/health", HealthController, :health
            end
            ```

        - `controllers/health_controller.ex`<br>
            ```ex
            defmodule ElixirPhoenixApiWeb.HealthController do
                use ElixirPhoenixApiWeb, :controller

                def health(conn, _params) do
                    conn
                    |> Plug.Conn.send_resp(
                    200,
                    Jason.encode!(%{
                        error: "ok"
                    })
                    )    
                end
            end
            ```

    - 各種ルート定義は、以下のコマンドで確認することもできる
        ```sh
        mix phx.routes
        ```
        ```sh
        Generated elixir_phoenix_api app
                page_path  GET  /                                      ElixirPhoenixApiWeb.PageController :index
                health_path  GET  /api/health                            ElixirPhoenixApiWeb.HealthController :health
        live_dashboard_path  GET  /dashboard                             Phoenix.LiveDashboard.PageLive :home
        live_dashboard_path  GET  /dashboard/:page                       Phoenix.LiveDashboard.PageLive :page
        live_dashboard_path  GET  /dashboard/:node/:page                 Phoenix.LiveDashboard.PageLive :page
                            *    /dev/mailbox                           Plug.Swoosh.MailboxPreview []
                websocket  WS   /live/websocket                        Phoenix.LiveView.Socket
                longpoll  GET  /live/longpoll                         Phoenix.LiveView.Socket
                longpoll  POST  /live/longpoll                         Phoenix.LiveView.Socket
        ```

1. Phoenix サーバーを起動する<br>
    ```sh
    cd ${PROJECT_NAME}
    mix phx.server
    ```

    - `mix phx.server` で、Web フレームワークである Phoenix のサーバーを起動している（`mix run` と同じようなもの）<br>
        この `mix phx.server` を実行する際には、他の mix コマンドと同様に `mix.exs` でプロジェクトが作成されている必要がある

    - デフォルトのポート番号は、`4000` になる

1. API にリクエストを出す
    ```sh
    # health check
    echo "[GET method] ヘルスチェック\n"
    curl http://0.0.0.0:4000/api/health
    echo "\n"
    ```

## ■ 参考サイト

- https://qiita.com/nako_9h_sleep/items/9d80f6cadfe341581df6
- https://qiita.com/akameco/items/1920e351328b1cc0ace3
- https://www.tech-note.info/entry/phoenix-4-routing-1