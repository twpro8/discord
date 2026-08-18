defmodule CallServerWeb.Router do
  use CallServerWeb, :router

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/api", CallServerWeb do
    pipe_through :api
  end
end
