use Mix.Config

config :elixir_ecto_postgresql, ElixirEctoPostgresql.Repo,
  adapter: Ecto.Adapters.Postgres,
  database: "elixir_ecto_postgresql_db",
#  database: "postgres",
  username: "postgres",
  password: "1234",
  hostname: "localhost",
#  hostname: "192.168.96.1",
  port: "5432"

config :elixir_ecto_postgresql, ecto_repos: [ElixirEctoPostgresql.Repo]
