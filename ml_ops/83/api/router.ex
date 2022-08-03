

  scope "/api", Blog do
    pipe_through :api
    resources "/posts", PostController, except: [:new, :edit]
  end