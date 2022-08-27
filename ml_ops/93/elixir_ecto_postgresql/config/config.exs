use Mix.Config

config :elixir_ecto_postgresql, ElixirEctoPostgresql.Repo,
  adapter: Ecto.Adapters.Postgres,
  database: "elixir_ecto_postgresql_db",
#  database: "postgres",
  username: "postgres",
  password: "1234",
  hostname: "localhost",
  port: "5432"

config :elixir_ecto_postgresql, ecto_repos: [ElixirEctoPostgresql.Repo]
