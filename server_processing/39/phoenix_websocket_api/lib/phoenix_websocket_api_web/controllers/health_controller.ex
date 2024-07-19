defmodule PhoenixWebsocketApiWeb.HealthController do
  use PhoenixWebsocketApiWeb, :controller

  def health(conn, _params) do
    json conn, Map.put(%{}, "health", "ok")
  end
end
