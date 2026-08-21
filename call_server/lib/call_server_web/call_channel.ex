defmodule CallServerWeb.CallChannel do
  use Phoenix.Channel

  require Logger

  @impl true
  def join("call:" <> call_id, _params, socket) do
    Logger.info("Joining call channel #{call_id}")

    {:ok, socket |> assign(:call_id, call_id)}
  end

  @impl true
  def handle_in("offer", %{"sdp" => sdp}, socket) do
    broadcast_from!(socket, "offer", %{sdp: sdp})
    {:noreply, socket}
  end

  @impl true
  def handle_in("answer", %{"sdp" => sdp}, socket) do
    broadcast_from!(socket, "answer", %{sdp: sdp})
    {:noreply, socket}
  end

  @impl true
  def handle_in("ice_candidate", %{"candidate" => candidate}, socket) do
    broadcast_from!(socket, "ice_candidate", %{candidate: candidate})
    {:noreply, socket}
  end
end
