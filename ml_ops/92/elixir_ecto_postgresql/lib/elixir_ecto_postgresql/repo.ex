defmodule ElixirEctoPostgresql.Repo do
  # `use` 構文を使用して `Ecto.Repo` モジュールを再定義している。
  use Ecto.Repo, 
    # `otp_app` は、`Ecto.Repo` モジュール内で定義されている変数で、どのアプリがデータベースへアクセスしているかを明示している。`use` 構文で `otp_app` の値を `:elixir_ecto_postgresql` に再定義しているので、`config.exs` 内 の `config :elixir_ecto_postgresql` が設定される
    otp_app: :elixir_ecto_postgresql
end
