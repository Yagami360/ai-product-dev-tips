defmodule ElixirPhoenixApiWeb.Router do
  # ルーティングするためのマクロ定義
  use ElixirPhoenixApiWeb, :router

  # ブラウザアクセス時の共通処理を定義した pipeline
  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_live_flash
    plug :put_root_layout, {ElixirPhoenixApiWeb.LayoutView, :root}
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  # ルートアクセス時（http:${IP_ADDRESS}:${PORT}/）以外のエンドポイントアクセス時の共通処理を定義した pipeline
  pipeline :api do
    plug :accepts, ["json"]
  end

  # ブラウザアクセス時のエンドポイント定義
  scope "/", ElixirPhoenixApiWeb do
    # ブラウザアクセス時の共通処理を定義した pipeline 内の plug 関数を全て実行
    pipe_through :browser

    # GET method を定義
    get "/", PageController, :index
  end

  # /api アクセス時のエンドポイント定義
  scope "/api", ElixirPhoenixApiWeb do
    # ルートアクセス時（http:${IP_ADDRESS}:${PORT}/）以外のエンドポイントアクセス時の共通処理を定義した pipeline 内の plug 関数を全て実行
    pipe_through :api

    # GET method
    get "/health", HealthController, :health
  end

  # Enables LiveDashboard only for development
  #
  # If you want to use the LiveDashboard in production, you should put
  # it behind authentication and allow only admins to access it.
  # If your application does not have an admins-only section yet,
  # you can use Plug.BasicAuth to set up some basic authentication
  # as long as you are also using SSL (which you should anyway).
  if Mix.env() in [:dev, :test] do
    import Phoenix.LiveDashboard.Router

    scope "/" do
      pipe_through :browser

      live_dashboard "/dashboard", metrics: ElixirPhoenixApiWeb.Telemetry
    end
  end

  # Enables the Swoosh mailbox preview in development.
  #
  # Note that preview only shows emails that were sent by the same
  # node running the Phoenix server.
  if Mix.env() == :dev do
    scope "/dev" do
      pipe_through :browser

      forward "/mailbox", Plug.Swoosh.MailboxPreview
    end
  end
end
