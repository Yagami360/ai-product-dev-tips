defmodule PhoenixWebsocketApiWeb.Proxy.WebSocket.Client do
  # WebSockex を使用する
  use WebSockex

  @type server :: pid | atom

  @type state :: %{required(:server) => server, required(:ref) => reference}

  @type options :: WebSockex.options()

  # WebSocket 通信を開始する。WebSocket.Supervisor の start_child から呼び出される
  # url: WebSocket 通信の URL（ws://xxx）
  def start_link(url, state, opts) do
    IO.inspect(["[WebSocket.Client/ start_link()] url:#{url}, state:#{}, opts:#{opts}"])
    WebSockex.start_link(url, __MODULE__, state, opts)
  end

  # WebSocket 通信の接続が確立されたときに呼び出されるコールバック関数
  def handle_connect(conn, state) do
    IO.inspect(["[WebSocket.Client/ handle_connect()] conn:#{conn}, state:#{state}", conn])

    # Store WebSockx.Conn to close the connection when the client browser shutdown its connection.
    state = Map.put(state, :conn, conn)
    {:ok, state}
  end

  # WebSocket 通信のメッセージ（フレーム）を受信したときに呼び出されるコールバック関数
  # フレームとしてテキストメッセージを受診した場合
  def handle_frame({:text, msg}, state) do
    IO.puts "[WebSocket.Client / handle_frame] Received a test message: #{msg}"
    {:ok, state}
  end

  # フレームとしてバイナリメッセージを受診した場合
  def handle_frame({:binary, msg}, state) do
    IO.puts "[WebSocket.Client / handle_frame] Received a binary message: #{msg}"
    {:ok, state}
  end

  # def handle_frame(frame, %{server: server, ref: ref} = state) do
  #   IO.inspect(["[WebSocket.Client/ handle_frame()] frame:", frame])

  #   send(server, {:send_frame, frame, %{ref: ref}})

  #   {:ok, state}
  # end

  # WebSocket 通信の切断が発生したときに呼び出されるコールバック関数
  def handle_disconnect(connection_status_map, %{server: server, ref: ref} = state) do
    IO.inspect([
      "[WebSocket.Client/ handle_disconnect()] connection_status_map:",
      connection_status_map
    ])

    IO.inspect(["[WebSocket.Client/ handle_disconnect()] state:", state])

    send(server, {:disconnect, %{ref: ref}})
    {:ok, state}
  end

  def handle_disconnect(connection_status_map, state) do
    IO.inspect([
      "[WebSocket.Client/ handle_disconnect()] connection_status_map:",
      connection_status_map
    ])

    IO.inspect(["[WebSocket.Client/ handle_disconnect()] state:", state])

    {:ok, state}
  end

  def handle_ping(:ping, %{server: server, ref: ref} = state) do
    IO.inspect(["[WebSocket.Client/ handle_ping()] :ping:", :ping])
    IO.inspect(["[WebSocket.Client/ handle_ping()] state:", state])

    send(server, {:send_frame, :ping, %{ref: ref}})
    {:reply, :pong, state}
  end

  def handle_ping({:ping, msg}, %{server: server, ref: ref} = state) do
    IO.inspect(["[WebSocket.Client/ handle_ping()] :ping:", :ping])
    IO.inspect(["[WebSocket.Client/ handle_ping()] msg:", msg])
    IO.inspect(["[WebSocket.Client/ handle_ping()] state:", state])

    send(server, {:send_frame, {:ping, msg}, %{ref: ref}})
    {:reply, {:pong, msg}, state}
  end

  def handle_ping(msg, state) do
    IO.inspect(["[WebSocket.Client/ handle_ping()] msg:", msg])
    IO.inspect(["[WebSocket.Client/ handle_ping()] state:", state])

    super(msg, state)
  end

  def handle_cast(:close, %{conn: conn} = state) do
    IO.inspect(["[WebSocket.Client/ handle_cast()] state:", state])

    WebSockex.Conn.close_socket(conn)
    {:ok, state}
  end

  def handle_cast(message, state) do
    IO.inspect(["[WebSocket.Client/ handle_cast()] message:", message])
    IO.inspect(["[WebSocket.Client/ handle_cast()] state:", state])

    {:ok, state}
  end

  def terminate(close_reason, _state) do
    IO.inspect(["[WebSocket.Client/ terminate()] close_reason:", close_reason])

    true
  end
end
