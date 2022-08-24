defmodule ElixirEctoPostgresql.Repo.Migrations.CreatePersonMigration do
  use Ecto.Migration

  def change do
    create table(:person_schema) do
      add :name, :string
      add :age, :integer
    end
  end
end
