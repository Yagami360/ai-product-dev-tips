defmodule ElixirPhoenixEcto.PersonSchema do
  # `use Ecto.Schema` で、Ecto.Schema を再定義することで、独自の Schema 定義を行っている
  use Ecto.Schema

  # PosgreSQL DB に反映するためのテーブル定義
  schema "person_table" do
    field :name, :string
    field :age, :integer
  end

  # changeset を行う関数
  def changeset(person_schema, params \\ %{}) do
    # Ecto.Changeset.cast() : changeset を作成する
    #   第１引数 : Ecto.Schema オブジェクト（今回は person_schema |> のようにパイプライン演算子で渡している）
    #   第２引数 : 値の登録や更新に使われるパラメーター
    #   第３引数 : 変更対象（changeset）の列
    # Ecto.Changeset.validate_required() : 
    #   第１引数 : Ecto.Changeset.cast() の戻り値
    #   第２引数 : validate（確認）する変更対象の列
    person_schema
    |> Ecto.Changeset.cast(params, [:age])
    |> Ecto.Changeset.validate_required([:age])
  end
end
