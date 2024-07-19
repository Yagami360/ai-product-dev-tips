defmodule PhoenixWebsocketApi.Repo do
  use Ecto.Repo,
    otp_app: :phoenix_websocket_api,
    adapter: Ecto.Adapters.Postgres
end
