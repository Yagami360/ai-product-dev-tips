defmodule PhoenixWebsocketApiWeb.Proxy.WebSocket.Supervisor do
  # DynamicSupervisor を使用する
  use DynamicSupervisor

  # PhoenixWebsocketApi.Application の上位 Supervisor から呼び出される
  def start_link(arg) do
    DynamicSupervisor.start_link(__MODULE__, arg, name: __MODULE__)
  end

  def init(_opts) do
    DynamicSupervisor.init(
      strategy: :one_for_one,
      extra_arguments: []
    )
  end

  # WebSocket 通信の子プロセスを起動する。Cowboy2Handler から呼び出される
  def start_child(url, %{server: server, ref: _ref} = state, opts \\ [])
      when is_pid(server) or is_atom(server) do
    # WebSockex を使用した WebSocket クライアントの start_link を呼び出し WebSocket 通信起動
    DynamicSupervisor.start_child(__MODULE__, {
      PhoenixWebsocketApiWeb.Proxy.WebSocket.Client,
      {url, state, opts}
    })
  end
end
