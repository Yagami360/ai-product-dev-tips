defmodule ElixirPhoenixApiWeb.PageController do
  use ElixirPhoenixApiWeb, :controller

  def index(conn, _params) do
    render(conn, "index.html")
  end
end
