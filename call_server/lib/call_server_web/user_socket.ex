defmodule CallServerWeb.UserSocket do
  use Phoenix.Socket

  require Logger

  channel "user:*", CallServerWeb.UserChannel
  channel "call:*", CallServerWeb.CallChannel

  def connect(_params, socket, _connect_info) do
    Logger.info("WebSocket connected!")

    {:ok, socket}
  end

  def id(_socket) do
    nil
  end
end
