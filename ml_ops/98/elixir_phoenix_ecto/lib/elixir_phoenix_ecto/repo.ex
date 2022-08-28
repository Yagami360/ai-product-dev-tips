defmodule ElixirPhoenixEcto.Repo do
  use Ecto.Repo,
    otp_app: :elixir_phoenix_ecto,
    adapter: Ecto.Adapters.Postgres
end
