defmodule PhoenixWebsocketApi.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    # Supervisor の子プロセス郡（supervision tree）
    children = [
      # Cowboy Websocket での Websocket 通信の Supervisor
      Plug.Cowboy.child_spec(
        scheme: :http,
        plug: PhoenixWebsocketApiWeb.PlugTop,
        options: [
          port: 4000,
          dispatch: [
            {:_,
              [
                {"/socket", PhoenixWebsocketApiWeb.Proxy.Cowboy2Handler, []},
                {:_, Plug.Cowboy.Handler, {PhoenixWebsocketApiWeb.Router, []}},
              ]
            }
          ]
        ]
      ),
      # API エンドポイントの Supervisor
      # PhoenixWebsocketApiWeb.Endpoint,
      # WebSockex での WebSocket 通信の Supervisor
      {PhoenixWebsocketApiWeb.Proxy.WebSocket.Supervisor, []},
      # 以下は、使用しないのでコメントアウト
      # PhoenixWebsocketApiWeb.Telemetry,
      # PhoenixWebsocketApi.Repo,
      # {DNSCluster, query: Application.get_env(:phoenix_websocket_api, :dns_cluster_query) || :ignore},
      # {Phoenix.PubSub, name: PhoenixWebsocketApi.PubSub},
      # Start the Finch HTTP client for sending emails
      # {Finch, name: PhoenixWebsocketApi.Finch},
      # Start a worker by calling: PhoenixWebsocketApi.Worker.start_link(arg)
      # {PhoenixWebsocketApi.Worker, arg},
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
