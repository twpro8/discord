defmodule CallServerWeb.UserSocket do
  use Phoenix.Socket

  require Logger

  def connect(_params, socket, _connect_info) do
    Logger.info("WebSocket connected!")

    {:ok, socket}
  end

  def id(_socket) do
    nil
  end
end
