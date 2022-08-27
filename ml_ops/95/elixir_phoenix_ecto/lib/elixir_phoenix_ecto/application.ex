defmodule ElixirPhoenixEcto.Application do
  # See https://hexdocs.pm/elixir/Application.html
  # for more information on OTP Applications
  @moduledoc false

  use Application

  @impl true
  def start(_type, _args) do
    children = [
      # Start the Ecto repository
      ElixirPhoenixEcto.Repo,
      # Start the Telemetry supervisor
      ElixirPhoenixEctoWeb.Telemetry,
      # Start the PubSub system
      {Phoenix.PubSub, name: ElixirPhoenixEcto.PubSub},
      # Start the Endpoint (http/https)
      ElixirPhoenixEctoWeb.Endpoint
      # Start a worker by calling: ElixirPhoenixEcto.Worker.start_link(arg)
      # {ElixirPhoenixEcto.Worker, arg}
    ]

    # See https://hexdocs.pm/elixir/Supervisor.html
    # for other strategies and supported options
    opts = [strategy: :one_for_one, name: ElixirPhoenixEcto.Supervisor]
    Supervisor.start_link(children, opts)
  end

  # Tell Phoenix to update the endpoint configuration
  # whenever the application is updated.
  @impl true
  def config_change(changed, _new, removed) do
    ElixirPhoenixEctoWeb.Endpoint.config_change(changed, removed)
    :ok
  end
end
