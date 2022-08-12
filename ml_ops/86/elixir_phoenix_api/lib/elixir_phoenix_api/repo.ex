defmodule ElixirPhoenixApi.Repo do
  use Ecto.Repo,
    otp_app: :elixir_phoenix_api,
    adapter: Ecto.Adapters.Postgres
end
