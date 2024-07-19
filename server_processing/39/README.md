# 【Elixir】 Phoenix + DynamicSupervisor + CowboyWebsocket + WebSockex を使用して Websocket 通信のプロキシーサーバーを構築する

## ■ 方法

1. 「[【Elixir】Phoenix を使用して簡単な REST API を作成する](https://github.com/Yagami360/ai-product-dev-tips/tree/master/ml_ops/86)」記載の方法に従って、Phoenix プロジェクトを作成する

1. プロジェクトディレクトリに移動する
    ```sh
    cd ${PROJECT_NAME}
    ```

1. PlugCowboy と WebSockex を追加する<br>
    `${PROJECT_NAME}/mix.exs` に DynamicSupervisor, PlugCowboy, WebSockex を追加し、インストールする

    ```elixir
    # mix.exs
    defp deps do
        [
            {:plug_cowboy, "~> 2.1"},
            {:websockex, "~> 0.4.0"},
            {:dynamic_supervisor, "~> 2.0"}
        ]
    end
    ```

    ```sh
    mix deps.get
    ```

1. WebSockex を使用した WebSocket クライアントのコードを作成する

1. DynamicSupervisor を使用した WebSocket プロセスの Supervisor のコードを作成する<br>
    `phoenix_websocket_api_web/proxy/websocket/supervisor.ex`

1. PlugCowboy を使用した xxx


    - Plug: Web サーバに対してクライアントがリクエストを発行した時起動されるハンドラを定義したモジュールで、API エンドポイントの pipeline で利用する

    - 各種 `websocket_*` コールバック関数の戻り値は、以下のような意味となる<br>
        - `{:ok, state}`: クライアントにメッセージを送らない場合
        - `{:reply, {:text, BINARY}, state}`: クライアントにテキストメッセージ（フレーム）を送る場合
        - `{:reply, {:text, BINARY}, state}`: クライアントにバイナリメッセージ（フレーム）を送る場合
        - `{:stop, state}`: 接続を切断する場合


    - 参考サイト
        - https://qiita.com/shufo/items/6ad1c2d51bca5a2e5f49#cowboy-websocket-behaviour


1. API エンドポイントを dispatch して、WebSocket クライアントとの通信を行う

    - xxx

1. API ルーターのコードを実装する<br>
    API のルーターを定義しているコード `${PROJECT_NAME}/lib/phoenix_websoket_api_web/router.ex` を修正する

    ```elixir
    ```
    
1. API コントローラーのコードを実装する<br>

    ```elixir
    ```

1. `lib/${PROJECT_NAME}/application.ex` に WebSocket プロセスの Supervisor を追加する<br>
    ```elixir
    defmodule PhoenixWebsocketApi.Application do
        # See https://hexdocs.pm/elixir/Application.html
        # for more information on OTP Applications
        @moduledoc false

        use Application

        @impl true
        def start(_type, _args) do
            # Supervisor の子プロセス郡（supervision tree）
            children = [
                PhoenixWebsocketApiWeb.Telemetry,
                PhoenixWebsocketApi.Repo,
                {DNSCluster, query: Application.get_env(:phoenix_websocket_api, :dns_cluster_query) || :ignore},
                {Phoenix.PubSub, name: PhoenixWebsocketApi.PubSub},
                # Start the Finch HTTP client for sending emails
                {Finch, name: PhoenixWebsocketApi.Finch},
                # Start a worker by calling: PhoenixWebsocketApi.Worker.start_link(arg)
                # {PhoenixWebsocketApi.Worker, arg},
                # Start to serve requests, typically the last entry
                PhoenixWebsocketApiWeb.Endpoint
            ]

            # See https://hexdocs.pm/elixir/Supervisor.html
            # for other strategies and supported options
            opts = [strategy: :one_for_one, name: PhoenixWebsocketApi.Supervisor]

            # Supervisor での子プロセス一覧を監視処理を起動
            Supervisor.start_link(children, opts)
        end

        # Tell Phoenix to update the endpoint configuration
        # whenever the application is updated.
        @impl true
        def config_change(changed, _new, removed) do
            PhoenixWebsocketApiWeb.Endpoint.config_change(changed, removed)
            :ok
        end
    end
    ```

    Supervisor とは、実際の処理を行う子プロセス郡（Supervision Tree）を監視するプロセス。


    - 参考サイト
        - https://ninenines.eu/docs/en/cowboy/2.12/guide/routing/


1. Phoenix サーバーを起動する<br>
    ```sh
    mix phx.server
    ```

1. ブラウザにアクセスする<br>
    ブラウザで以下の URL にアクセスし、うまく WebSocket 通信のプロキシーができていることを確認する
    ```sh
    open http://0.0.0.0:4000
    ```
