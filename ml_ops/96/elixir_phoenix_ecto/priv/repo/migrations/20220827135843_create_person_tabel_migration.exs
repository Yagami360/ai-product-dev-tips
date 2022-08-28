defmodule ElixirPhoenixEcto.Repo.Migrations.CreatePersonTabelMigration do
  use Ecto.Migration

  def change do
    create table(:person_table) do
      add :name, :string
      add :age, :integer
    end
  end
end
