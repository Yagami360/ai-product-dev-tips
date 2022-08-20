defmodule ElixirEctoPostgresqlTest do
  use ExUnit.Case
  doctest ElixirEctoPostgresql

  test "greets the world" do
    assert ElixirEctoPostgresql.hello() == :world
  end
end
