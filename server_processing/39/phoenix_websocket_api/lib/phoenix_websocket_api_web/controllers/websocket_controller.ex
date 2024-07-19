defmodule PhoenixWebsocketApiWeb.WebSocketController do
  use PhoenixWebsocketApiWeb, :controller

  def socket(conn, _params) do
    IO.inspect(["[WebSocketController / socket] conn:", conn])
    IO.inspect(["[WebSocketController / socket] _params:", _params])

    json conn, Map.put(%{}, "health", "ok")
  end
end
