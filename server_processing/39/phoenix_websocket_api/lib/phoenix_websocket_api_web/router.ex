defmodule PhoenixWebsocketApiWeb.Router do
  use PhoenixWebsocketApiWeb, :router

  # ブラウザアクセス時の共通処理を定義した pipeline
  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_live_flash
    plug :put_root_layout, html: {PhoenixWebsocketApiWeb.Layouts, :root}
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  # ルートアクセス時（http:${IP_ADDRESS}:${PORT}/）以外のエンドポイントアクセス時の共通処理を定義した pipeline
  pipeline :api do
    plug :accepts, ["json"]
  end

  # ブラウザアクセス時のエンドポイント定義
  scope "/", PhoenixWebsocketApiWeb do
    pipe_through :browser

    get "/", PageController, :home
    # get "/socket", WebSocketController, :socket
  end

  # /api アクセス時のエンドポイント定義
  scope "/api", PhoenixWebsocketApiWeb do
      # ルートアクセス時（http:${IP_ADDRESS}:${PORT}/）以外のエンドポイントアクセス時の共通処理を定義した pipeline 内の plug 関数を全て実行
      pipe_through :api

      # GET method
      get "/health", HealthController, :health
  end

  # Enable LiveDashboard and Swoosh mailbox preview in development
  if Application.compile_env(:phoenix_websocket_api, :dev_routes) do
    # If you want to use the LiveDashboard in production, you should put
    # it behind authentication and allow only admins to access it.
    # If your application does not have an admins-only section yet,
    # you can use Plug.BasicAuth to set up some basic authentication
    # as long as you are also using SSL (which you should anyway).
    import Phoenix.LiveDashboard.Router

    scope "/dev" do
      pipe_through :browser

      live_dashboard "/dashboard", metrics: PhoenixWebsocketApiWeb.Telemetry
      forward "/mailbox", Plug.Swoosh.MailboxPreview
    end
  end
end
