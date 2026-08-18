defmodule CallServerWeb.UserSocketTest do
  use ExUnit.Case, async: true

  import Phoenix.ChannelTest

  @endpoint CallServerWeb.Endpoint

  test "accepts a websocket connection" do
    assert {:ok, socket} = connect(CallServerWeb.UserSocket, %{})
    assert %Phoenix.Socket{} = socket
  end
end
