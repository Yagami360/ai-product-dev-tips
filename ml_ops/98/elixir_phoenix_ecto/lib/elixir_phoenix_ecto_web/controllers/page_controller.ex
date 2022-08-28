defmodule ElixirPhoenixEctoWeb.PageController do
  use ElixirPhoenixEctoWeb, :controller

  def index(conn, _params) do
    render(conn, "index.html")
  end
end
