defmodule ElixirEctoPostgresql.PersonSchema do
  # `use Ecto.Schema` で、Ecto.Schema を再定義することで、独自の Schema 定義を行っている
  use Ecto.Schema

  # PosgreSQL DB に反映するためのテーブル定義
  schema "person_schema" do
    field :name, :string
    field :age, :integer
  end
end
