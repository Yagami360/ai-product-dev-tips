# https://ninenines.eu/docs/en/cowboy/2.6/guide/ws_handlers/
defmodule PhoenixWebsocketApiWeb.Proxy.Cowboy2Handler do
  import Plug.Conn
  alias PhoenixWebsocketApiWeb.Proxy.WebSocket

  # Cowboy Websocket に従ったハンドラ（コールバック関数）定義のモジュール
  @behaviour :cowboy_websocket

  # 定数
  @websocket_url Application.get_env(:phoenix_websocket_proxy_server, :websocket_url)
  @connection Plug.Cowboy.Conn

  # cowboy のコールバック関数全てでリクエストを受け取ったときに呼び出されるコールバック関数
  def init(req, state) do
    IO.inspect(["[Cowboy2Handler / init] req:", req])
    IO.inspect(["[Cowboy2Handler / init] state:", state])

    # ? Plug.Cowboy を使用して xxx
    # conn =
    #   Plug.Cowboy.Conn.conn(req)
    #   |> HTTPPipeline.call([])

      # Cowboy Websocket のオプションを設定
    opts = %{idle_timeout: 60000}

    # :cowboy_websocket を返すと Websocket へ Upgrade される
    {:cowboy_websocket, req, state, opts}
  end

  # クライアントとの WebSocet 通信が接続した直後に呼び出される
  def websocket_init(state) do
    IO.inspect(["[Cowboy2Handler / websocket_init] state:", state])

    # クライアント（ブラウザ）にフレーム送信
    # {:reply, {:text, "start"}, state}

    # WebSockex を使用した WebSocket 通信を開始
    # ローカル環境で起動した streamlit サーバーからの WebSocket 通信をプロキシーしてブラウザに送信
    # IO.inspect(["[Cowboy2Handler / websocket_init] @websocket_url:", @websocket_url])
    # WebSocket.Supervisor.start_child(
    #   @websocket_url,
    #   %{server: self(), ref: :websocket}
    # )

    # WebSocket.Supervisor.start_child(
    #   "ws://localhost:4000/socket",
    #   %{server: self(), ref: :websocket}
    # )
  end

  # クライアントがメッセージを送ると呼び出される構築関数
  def websocket_handle(frame, state) do
    IO.inspect(["[Cowboy2Handler / websocket_handle] frame:", frame])

    # :ping = frame
    # :pong = frame
    # {:text, BINARY} = frame
    # {:binary, BINARY} = frame
    # {:ping, BINARY} = frame
    # {:pong, BINARY} = frame
    # ...
    # クライアントにテキストメッセージを送る
    {:reply, {:text, "duumy"}, state}
  end

  # 定期的にメッセージを送らないとコネクションがタイムアウトするので pingメッセージを送る
  def websocket_handle(:ping, state) do
    IO.inspect(["[Cowboy2Handler / websocket_handle] :ping"])

    # pingメッセージにpongメッセージを返す
    {:reply, :pong, state}
  end

  def websocket_handle({:ping, frame}, state) do
      {:reply, {:pong, frame}, state}
  end

  def websocket_handle(:pong, state) do
      # クライアントにメッセージを送らない
      {:ok, state}
  end

  def websocket_handle({:pong, _frame}, state) do
      # クライアントにメッセージを送らない
      {:ok, state}
  end

  def websocket_info(:ping, state) do
      # Process.send_after(self(), :ping, 10_000)
      # クライアントに ping メッセージを送る
      {:reply, :ping, state}
  end

  def websocket_info(message, state) do
      # クライアントにテキストメッセージを送る
      {:reply, {:text, message}, state}
  end

  def terminate(reason, req, state) do
      #...
      :ok
  end

end
