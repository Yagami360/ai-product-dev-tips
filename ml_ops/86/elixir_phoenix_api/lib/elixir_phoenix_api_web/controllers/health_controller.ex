defmodule ElixirPhoenixApiWeb.HealthController do
  use ElixirPhoenixApiWeb, :controller

  def health(conn, _params) do
    json conn, Map.put(%{}, "health", "ok")
  end
end
